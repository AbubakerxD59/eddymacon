<?php
/**
 * Admin: list joinings / bookings for an event.
 * GET ?event_id=123
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

$eventId = (int) ($_GET['event_id'] ?? 0);
if ($eventId <= 0) {
    api_error('Invalid event id', 422);
}

try {
    $pdo = db();
    events_ensure_schema($pdo);

    $evt = $pdo->prepare('SELECT id, title FROM events WHERE id = ? LIMIT 1');
    $evt->execute([$eventId]);
    $event = $evt->fetch();
    if (!$event) {
        api_error('Event not found', 404);
    }

    $stmt = $pdo->prepare(
        'SELECT id, event_id, customer_name, phone_number, email_address, created_at
         FROM event_bookings
         WHERE event_id = ?
         ORDER BY created_at DESC, id DESC'
    );
    $stmt->execute([$eventId]);
    $rows = $stmt->fetchAll();

    foreach ($rows as &$row) {
        $row['id'] = (int) $row['id'];
        $row['event_id'] = (int) $row['event_id'];
    }
    unset($row);

    api_json([
        'ok'       => true,
        'event'    => [
            'id'    => (int) $event['id'],
            'title' => (string) $event['title'],
        ],
        'bookings' => $rows,
    ]);
} catch (Throwable $e) {
    api_error('Could not load joinings', 500);
}
