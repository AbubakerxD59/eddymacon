<?php
/**
 * Admin: save site content JSON.
 * POST JSON body: { data: { ... } } or raw content object.
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../auth/session.php';
require_once __DIR__ . '/schema.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_error('Method not allowed', 405);
}

if (!admin_is_authenticated()) {
    api_error('Unauthorized', 401);
}

$raw = file_get_contents('php://input') ?: '';
$payload = json_decode($raw, true);
if (!is_array($payload)) {
    api_error('Invalid JSON body', 422);
}

$data = $payload['data'] ?? $payload;
if (!is_array($data) || $data === []) {
    api_error('Content data is required', 422);
}

// Normalize nested sections if present
foreach (['hero', 'approach', 'navigation', 'investments', 'contact', 'socials', 'ai'] as $key) {
    if (array_key_exists($key, $data) && !is_array($data[$key])) {
        api_error("Invalid section: {$key}", 422);
    }
}

try {
    $pdo = db();
    content_ensure_schema($pdo);

    // Load existing so blank image fields do not wipe stored filenames
    $existing = [];
    $cur = $pdo->prepare('SELECT data FROM site_content WHERE id = ? LIMIT 1');
    $cur->execute(['macon_v1']);
    $row = $cur->fetch();
    if ($row) {
        $existing = $row['data'];
        if (is_string($existing)) {
            $existing = json_decode($existing, true) ?: [];
        }
        if (!is_array($existing)) {
            $existing = [];
        }
    }

    foreach (['hero', 'approach'] as $section) {
        if (!isset($data[$section]) || !is_array($data[$section])) {
            continue;
        }
        $img = isset($data[$section]['image']) ? trim((string) $data[$section]['image']) : '';
        if ($img === '' && !empty($existing[$section]['image'])) {
            $img = (string) $existing[$section]['image'];
        }
        // Normalize "uploads/foo.jpg" or bare filename into uploads/ path when needed
        if ($img !== '' && !preg_match('#^(https?:)?//#i', $img) && !str_starts_with($img, 'data:') && !str_contains($img, '/')) {
            $img = 'uploads/' . ltrim($img, '/');
        }
        $data[$section]['image'] = $img;
    }

    $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        api_error('Could not encode content', 500);
    }

    $stmt = $pdo->prepare(
        'INSERT INTO site_content (id, data) VALUES (?, ?)
         ON DUPLICATE KEY UPDATE data = VALUES(data), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute(['macon_v1', $json]);

    api_json([
        'ok'   => true,
        'id'   => 'macon_v1',
        'data' => $data,
    ]);
} catch (Throwable $e) {
    api_error('Could not save content', 500);
}
