<?php
/**
 * Public: join / book an event.
 * POST JSON: event_id, customer_name (or full_name), phone_number (or phone), email_address? (or email)
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

$eventId = (int) ($data['event_id'] ?? 0);
$name = trim((string) ($data['customer_name'] ?? $data['full_name'] ?? $data['name'] ?? ''));
$phone = trim((string) ($data['phone_number'] ?? $data['phone'] ?? ''));
$email = trim((string) ($data['email_address'] ?? $data['email'] ?? ''));

if ($eventId <= 0) {
    api_error('Event is required', 422);
}

if ($name === '' || $phone === '') {
    api_error('Full name and phone number are required', 422);
}

if (mb_strlen($name) > 191 || mb_strlen($phone) > 50 || mb_strlen($email) > 191) {
    api_error('One or more fields are too long', 422);
}

if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    api_error('Please enter a valid email address', 422);
}

try {
    $pdo = db();
    events_ensure_schema($pdo);

    $evt = $pdo->prepare(
        'SELECT id FROM events WHERE id = ? AND status = \'published\' LIMIT 1'
    );
    $evt->execute([$eventId]);
    if (!$evt->fetch()) {
        api_error('Event not found', 404);
    }

    $stmt = $pdo->prepare(
        'INSERT INTO event_bookings (event_id, customer_name, phone_number, email_address)
         VALUES (:event_id, :customer_name, :phone_number, :email_address)'
    );
    $stmt->execute([
        ':event_id'       => $eventId,
        ':customer_name'  => $name,
        ':phone_number'   => $phone,
        ':email_address'  => $email !== '' ? $email : null,
    ]);

    api_json([
        'ok' => true,
        'id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Throwable $e) {
    api_error('Could not submit your registration. Please try again later.', 500);
}
