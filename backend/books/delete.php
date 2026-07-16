<?php
/**
 * Admin: delete a book.
 * POST/DELETE JSON: { id }
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/../auth/session.php';
require_once __DIR__ . '/schema.php';

api_headers();

if (!in_array($_SERVER['REQUEST_METHOD'], ['POST', 'DELETE'], true)) {
    api_error('Method not allowed', 405);
}

if (!admin_is_authenticated()) {
    api_error('Unauthorized', 401);
}

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

$id = (int) ($data['id'] ?? ($_GET['id'] ?? 0));
if ($id <= 0) {
    api_error('Invalid book id', 422);
}

try {
    $pdo = db();
    books_ensure_schema($pdo);

    $stmt = $pdo->prepare('DELETE FROM books WHERE id = :id');
    $stmt->execute([':id' => $id]);

    api_json([
        'ok'      => true,
        'deleted' => $stmt->rowCount() > 0,
    ]);
} catch (Throwable $e) {
    api_error('Could not delete book', 500);
}
