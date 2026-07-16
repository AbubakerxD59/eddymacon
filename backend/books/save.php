<?php
/**
 * Admin: create or update a book.
 * POST JSON: { id?, title, description?, sale_url, cover_image?, is_featured?, sort_order? }
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
$data = json_decode($raw, true);
if (!is_array($data)) {
    api_error('Invalid JSON body', 422);
}

$id = (int) ($data['id'] ?? 0);
$title = trim((string) ($data['title'] ?? ''));
$description = trim((string) ($data['description'] ?? ''));
$saleUrl = trim((string) ($data['sale_url'] ?? ''));
$coverImage = trim((string) ($data['cover_image'] ?? ''));
$isFeatured = !empty($data['is_featured']) ? 1 : 0;
$sortOrder = (int) ($data['sort_order'] ?? 0);

if ($title === '' || $saleUrl === '') {
    api_error('Title and sale link are required', 422);
}

if (mb_strlen($title) > 255) {
    api_error('Title is too long', 422);
}

if (mb_strlen($saleUrl) > 512) {
    api_error('Sale link is too long', 422);
}

if (!preg_match('#^https?://#i', $saleUrl)) {
    api_error('Sale link must start with http:// or https://', 422);
}

if ($coverImage !== '' && !preg_match('#^(https?:)?//#i', $coverImage) && !str_starts_with($coverImage, 'data:') && !str_contains($coverImage, '/')) {
    $coverImage = 'uploads/' . ltrim($coverImage, '/');
}

if (mb_strlen($coverImage) > 512) {
    api_error('Cover image path is too long', 422);
}

try {
    $pdo = db();
    books_ensure_schema($pdo);
    $pdo->beginTransaction();

    if ($isFeatured === 1) {
        $pdo->exec('UPDATE books SET is_featured = 0');
    }

    if ($id > 0) {
        $check = $pdo->prepare('SELECT id, cover_image FROM books WHERE id = ? LIMIT 1');
        $check->execute([$id]);
        $existing = $check->fetch();
        if (!$existing) {
            $pdo->rollBack();
            api_error('Book not found', 404);
        }

        if ($coverImage === '' && !empty($existing['cover_image'])) {
            $coverImage = (string) $existing['cover_image'];
        }

        $stmt = $pdo->prepare(
            'UPDATE books
             SET title = :title,
                 description = :description,
                 sale_url = :sale_url,
                 cover_image = :cover_image,
                 is_featured = :is_featured,
                 sort_order = :sort_order
             WHERE id = :id'
        );
        $stmt->execute([
            ':title'        => $title,
            ':description'  => $description !== '' ? $description : null,
            ':sale_url'     => $saleUrl,
            ':cover_image'  => $coverImage !== '' ? $coverImage : null,
            ':is_featured'  => $isFeatured,
            ':sort_order'   => $sortOrder,
            ':id'           => $id,
        ]);
        $bookId = $id;
    } else {
        $stmt = $pdo->prepare(
            'INSERT INTO books (title, description, sale_url, cover_image, is_featured, sort_order)
             VALUES (:title, :description, :sale_url, :cover_image, :is_featured, :sort_order)'
        );
        $stmt->execute([
            ':title'        => $title,
            ':description'  => $description !== '' ? $description : null,
            ':sale_url'     => $saleUrl,
            ':cover_image'  => $coverImage !== '' ? $coverImage : null,
            ':is_featured'  => $isFeatured,
            ':sort_order'   => $sortOrder,
        ]);
        $bookId = (int) $pdo->lastInsertId();
    }

    $pdo->commit();

    $get = $pdo->prepare(
        'SELECT id, title, description, sale_url, cover_image, is_featured, sort_order, created_at, updated_at
         FROM books WHERE id = ? LIMIT 1'
    );
    $get->execute([$bookId]);
    $book = $get->fetch();
    if ($book) {
        $book['id'] = (int) $book['id'];
        $book['is_featured'] = (int) $book['is_featured'] === 1;
        $book['sort_order'] = (int) $book['sort_order'];
    }

    api_json([
        'ok'   => true,
        'book' => $book,
    ]);
} catch (Throwable $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    api_error('Could not save book', 500);
}
