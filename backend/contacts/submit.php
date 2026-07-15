<?php
/**
 * Public contact form submit.
 * POST JSON or form: name, email, phone, message
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/schema.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_error('Method not allowed', 405);
}

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

$name = trim((string) ($data['name'] ?? ''));
$email = trim((string) ($data['email'] ?? ''));
$phone = trim((string) ($data['phone'] ?? ''));
$message = trim((string) ($data['message'] ?? ''));

if ($name === '' || $email === '' || $phone === '' || $message === '') {
    api_error('All fields are required', 422);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    api_error('Please enter a valid email address', 422);
}

if (mb_strlen($name) > 191 || mb_strlen($email) > 191 || mb_strlen($phone) > 50) {
    api_error('One or more fields are too long', 422);
}

try {
    $pdo = db();
    contacts_ensure_schema($pdo);

    $stmt = $pdo->prepare(
        'INSERT INTO contacts (name, email, phone, message) VALUES (:name, :email, :phone, :message)'
    );
    $stmt->execute([
        ':name'    => $name,
        ':email'   => $email,
        ':phone'   => $phone,
        ':message' => $message,
    ]);

    api_json([
        'ok' => true,
        'id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Throwable $e) {
    api_error('Could not save your message. Please try again later.', 500);
}
