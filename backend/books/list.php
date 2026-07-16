<?php
/**
 * List books for public site and admin.
 * Public: all books ordered by featured, then sort_order.
 * Admin session not required (sale links are public).
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
    books_ensure_schema($pdo);

    $rows = $pdo->query(
        'SELECT id, title, description, sale_url, cover_image, is_featured, sort_order, created_at, updated_at
         FROM books
         ORDER BY is_featured DESC, sort_order ASC, id ASC'
    )->fetchAll();

    foreach ($rows as &$row) {
        $row['id'] = (int) $row['id'];
        $row['is_featured'] = (int) $row['is_featured'] === 1;
        $row['sort_order'] = (int) $row['sort_order'];
    }
    unset($row);

    api_json([
        'ok'    => true,
        'books' => $rows,
    ]);
} catch (Throwable $e) {
    api_error('Could not load books', 500);
}
