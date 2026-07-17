<?php
/**
 * Public: submit a book-me / hire request.
 * POST JSON: full_name, email_address (or email), phone_number (or phone),
 *            address, booking_date (or date), booking_time (or time)
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

$name = trim((string) ($data['full_name'] ?? $data['name'] ?? ''));
$email = trim((string) ($data['email_address'] ?? $data['email'] ?? ''));
$phone = trim((string) ($data['phone_number'] ?? $data['phone'] ?? ''));
$address = trim((string) ($data['address'] ?? ''));
$date = trim((string) ($data['booking_date'] ?? $data['date'] ?? ''));
$time = trim((string) ($data['booking_time'] ?? $data['time'] ?? ''));

if ($name === '' || $email === '' || $phone === '' || $address === '' || $date === '' || $time === '') {
    api_error('All fields are required', 422);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    api_error('Please enter a valid email address', 422);
}

if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    api_error('Please enter a valid date', 422);
}

// Accept HH:MM or HH:MM:SS
if (!preg_match('/^\d{1,2}:\d{2}(:\d{2})?$/', $time)) {
    api_error('Please enter a valid time', 422);
}

$timeParts = explode(':', $time);
$h = (int) $timeParts[0];
$m = (int) $timeParts[1];
$s = isset($timeParts[2]) ? (int) $timeParts[2] : 0;
if ($h < 0 || $h > 23 || $m < 0 || $m > 59 || $s < 0 || $s > 59) {
    api_error('Please enter a valid time', 422);
}
$timeNormalized = sprintf('%02d:%02d:%02d', $h, $m, $s);

$dt = DateTimeImmutable::createFromFormat('Y-m-d', $date);
if (!$dt || $dt->format('Y-m-d') !== $date) {
    api_error('Please enter a valid date', 422);
}

if (mb_strlen($name) > 191 || mb_strlen($email) > 191 || mb_strlen($phone) > 50 || mb_strlen($address) > 512) {
    api_error('One or more fields are too long', 422);
}

try {
    $pdo = db();
    book_me_ensure_schema($pdo);

    $stmt = $pdo->prepare(
        'INSERT INTO book_me (full_name, email_address, phone_number, address, booking_date, booking_time)
         VALUES (:full_name, :email_address, :phone_number, :address, :booking_date, :booking_time)'
    );
    $stmt->execute([
        ':full_name'     => $name,
        ':email_address' => $email,
        ':phone_number'  => $phone,
        ':address'       => $address,
        ':booking_date'  => $date,
        ':booking_time'  => $timeNormalized,
    ]);

    api_json([
        'ok' => true,
        'id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Throwable $e) {
    api_error('Could not submit your request. Please try again later.', 500);
}
