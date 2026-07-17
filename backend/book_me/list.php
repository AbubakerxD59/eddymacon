<?php
/**
 * Admin: list book-me / hire requests.
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../auth/session.php';
require_once __DIR__ . '/schema.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    api_error('Method not allowed', 405);
}

if (!admin_is_authenticated()) {
    api_error('Unauthorized', 401);
}

try {
    $pdo = db();
    book_me_ensure_schema($pdo);

    $rows = $pdo->query(
        'SELECT id, full_name, email_address, phone_number, address, booking_date, booking_time, created_at
         FROM book_me
         ORDER BY created_at DESC, id DESC'
    )->fetchAll();

    api_json([
        'ok'      => true,
        'book_me' => $rows,
    ]);
} catch (Throwable $e) {
    api_error('Could not load book-me requests', 500);
}
