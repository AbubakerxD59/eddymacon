<?php
/**
 * Public: get site content JSON.
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/schema.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    api_error('Method not allowed', 405);
}

try {
    $pdo = db();
    content_ensure_schema($pdo);

    $stmt = $pdo->prepare('SELECT data FROM site_content WHERE id = ? LIMIT 1');
    $stmt->execute(['macon_v1']);
    $row = $stmt->fetch();

    if (!$row) {
        $data = content_default_data();
    } else {
        $data = $row['data'];
        if (is_string($data)) {
            $data = json_decode($data, true);
        }
        if (!is_array($data)) {
            $data = content_default_data();
        }
    }

    api_json([
        'ok'   => true,
        'id'   => 'macon_v1',
        'data' => $data,
    ]);
} catch (Throwable $e) {
    api_error('Could not load content', 500);
}
