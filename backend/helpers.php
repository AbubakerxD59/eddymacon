<?php
/**
 * Shared JSON API helpers (CORS + response).
 */

declare(strict_types=1);

function api_headers(): void
{
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
}

function api_json(mixed $data, int $status = 200): void
{
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function api_error(string $message, int $status = 400, array $extra = []): void
{
    api_json(array_merge(['ok' => false, 'error' => $message], $extra), $status);
}

/**
 * Allow basic rich-text tags for event descriptions (Quill HTML),
 * including safe text / background colors.
 */
function sanitize_rich_text(string $html): string
{
    $html = trim($html);
    if ($html === '' || $html === '<p><br></p>' || $html === '<p></p>') {
        return '';
    }

    if (!class_exists('DOMDocument')) {
        $allowed = '<p><br><strong><b><em><i><u><s><ol><ul><li><a><h1><h2><h3><h4><blockquote><span>';
        return trim(strip_tags($html, $allowed));
    }

    $dom = new DOMDocument();
    $prev = libxml_use_internal_errors(true);
    $dom->loadHTML(
        '<?xml encoding="UTF-8"><div id="em-rt-root">' . $html . '</div>',
        LIBXML_HTML_NODEFDTD | LIBXML_NOERROR | LIBXML_NOWARNING
    );
    libxml_clear_errors();
    libxml_use_internal_errors($prev);

    $root = $dom->getElementById('em-rt-root');
    if (!$root instanceof DOMElement) {
        return '';
    }

    sanitize_rich_text_node($root);

    $out = '';
    foreach ($root->childNodes as $child) {
        $out .= $dom->saveHTML($child);
    }

    return trim($out);
}

function sanitize_rich_text_styles(string $style): string
{
    $safe = [];
    foreach (explode(';', $style) as $part) {
        $part = trim($part);
        if ($part === '' || !str_contains($part, ':')) {
            continue;
        }
        [$prop, $val] = array_map('trim', explode(':', $part, 2));
        $prop = strtolower($prop);
        $val = trim($val);
        if (!in_array($prop, ['color', 'background-color', 'font-size'], true)) {
            continue;
        }
        if ($val === '' || preg_match('/expression|url\s*\(|javascript|@import|behavior/i', $val)) {
            continue;
        }
        if ($prop === 'font-size') {
            if (!preg_match('/^\d+(\.\d+)?(px|em|rem|%)$/i', $val)) {
                continue;
            }
        } elseif (!preg_match('/^(#[0-9a-f]{3,8}|rgba?\(\s*[\d.\s%,]+\s*\)|hsla?\(\s*[\d.\s%,]+\s*\)|[a-z]+)$/i', $val)) {
            continue;
        }
        $safe[] = $prop . ': ' . $val;
    }

    return implode('; ', $safe);
}

function sanitize_rich_text_classes(string $class): string
{
    $allowed = [
        'ql-size-small',
        'ql-size-large',
        'ql-size-huge',
    ];
    $kept = [];
    foreach (preg_split('/\s+/', trim($class)) ?: [] as $token) {
        $token = strtolower($token);
        if (in_array($token, $allowed, true)) {
            $kept[] = $token;
        }
    }

    return implode(' ', array_unique($kept));
}

function sanitize_rich_text_node(DOMNode $node): void
{
    static $allowed = [
        'div', 'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's',
        'ol', 'ul', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'span',
    ];

    $children = [];
    foreach ($node->childNodes as $child) {
        $children[] = $child;
    }

    foreach ($children as $child) {
        if ($child->nodeType === XML_ELEMENT_NODE) {
            /** @var DOMElement $child */
            $tag = strtolower($child->tagName);

            if ($tag === 'div' && $child->getAttribute('id') === 'em-rt-root') {
                sanitize_rich_text_node($child);
                continue;
            }

            if (!in_array($tag, $allowed, true) || $tag === 'div') {
                $parent = $child->parentNode;
                if ($parent) {
                    // Drop dangerous tags entirely (don't keep their text/content)
                    $stripEntirely = [
                        'script', 'style', 'iframe', 'object', 'embed',
                        'form', 'input', 'button', 'textarea', 'link', 'meta',
                    ];
                    if (in_array($tag, $stripEntirely, true)) {
                        $parent->removeChild($child);
                    } else {
                        while ($child->firstChild) {
                            $parent->insertBefore($child->firstChild, $child);
                        }
                        $parent->removeChild($child);
                    }
                }
                continue;
            }

            $keep = [];
            if ($child->hasAttributes()) {
                foreach (iterator_to_array($child->attributes) as $attr) {
                    $name = strtolower($attr->name);
                    $value = $attr->value;

                    if ($tag === 'a' && $name === 'href') {
                        $href = trim(html_entity_decode($value, ENT_QUOTES | ENT_HTML5, 'UTF-8'));
                        if ($href !== '' && preg_match('#^(https?:|mailto:|/|#)#i', $href)) {
                            $keep['href'] = $href;
                            $keep['target'] = '_blank';
                            $keep['rel'] = 'noopener noreferrer';
                        }
                        continue;
                    }

                    if ($name === 'style') {
                        $safeStyle = sanitize_rich_text_styles($value);
                        if ($safeStyle !== '') {
                            $keep['style'] = $safeStyle;
                        }
                        continue;
                    }

                    if ($name === 'class') {
                        $safeClass = sanitize_rich_text_classes($value);
                        if ($safeClass !== '') {
                            $keep['class'] = $safeClass;
                        }
                    }
                }
            }

            while ($child->hasAttributes()) {
                $child->removeAttribute($child->attributes->item(0)->name);
            }
            foreach ($keep as $name => $value) {
                $child->setAttribute($name, $value);
            }
        }

        if ($child->parentNode) {
            sanitize_rich_text_node($child);
        }
    }
}
