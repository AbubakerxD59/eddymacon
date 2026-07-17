<?php
/**
 * Ensure site_content table exists and is seeded with defaults.
 */

declare(strict_types=1);

function content_default_data(): array
{
    $path = __DIR__ . '/defaults.json';
    if (!is_file($path)) {
        throw new RuntimeException('Missing backend/content/defaults.json');
    }

    $raw = file_get_contents($path);
    $data = json_decode((string) $raw, true);
    if (!is_array($data)) {
        throw new RuntimeException('Invalid defaults.json');
    }

    return $data;
}

function content_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS site_content (
            id VARCHAR(64) NOT NULL PRIMARY KEY,
            data JSON NOT NULL,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    $stmt = $pdo->prepare('SELECT id FROM site_content WHERE id = ? LIMIT 1');
    $stmt->execute(['macon_v1']);
    if (!$stmt->fetch()) {
        $defaults = content_default_data();
        $ins = $pdo->prepare('INSERT INTO site_content (id, data) VALUES (?, ?)');
        $ins->execute(['macon_v1', json_encode($defaults, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)]);
        return;
    }

    content_migrate_nav_events($pdo);
}

/**
 * Replace INVESTMENTS nav link with EVENTS → events/
 */
function content_migrate_nav_events(PDO $pdo): void
{
    $stmt = $pdo->prepare('SELECT data FROM site_content WHERE id = ? LIMIT 1');
    $stmt->execute(['macon_v1']);
    $row = $stmt->fetch();
    if (!$row) {
        return;
    }

    $data = json_decode((string) $row['data'], true);
    if (!is_array($data) || !isset($data['navigation']['links']) || !is_array($data['navigation']['links'])) {
        return;
    }

    $changed = false;
    foreach ($data['navigation']['links'] as &$link) {
        if (!is_array($link)) {
            continue;
        }
        $label = strtoupper(trim((string) ($link['label'] ?? '')));
        $href = (string) ($link['href'] ?? '');
        if ($label === 'INVESTMENTS' || $href === '#investments') {
            $link['label'] = 'EVENTS';
            $link['href'] = 'events/';
            $changed = true;
        }
    }
    unset($link);

    if (!$changed) {
        return;
    }

    $upd = $pdo->prepare('UPDATE site_content SET data = ? WHERE id = ?');
    $upd->execute([
        json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
        'macon_v1',
    ]);
}
