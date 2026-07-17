<?php
/**
 * Admin: create or update an event (+ media rows).
 * POST JSON: {
 *   id?, title, description?, cover_image?,
 *   event_date, start_time, end_time, price?, location?, type?, webinar_link?, status?,
 *   media?: [{ type?, media_url, sort_order? }]
 * }
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
$description = sanitize_rich_text(trim((string) ($data['description'] ?? '')));
$coverImage = trim((string) ($data['cover_image'] ?? ''));
$eventDate = trim((string) ($data['event_date'] ?? ''));
$startTime = trim((string) ($data['start_time'] ?? ''));
$endTime = trim((string) ($data['end_time'] ?? ''));
$location = trim((string) ($data['location'] ?? ''));
$type = strtolower(trim((string) ($data['type'] ?? 'physical')));
$webinarLink = trim((string) ($data['webinar_link'] ?? ''));
$status = strtolower(trim((string) ($data['status'] ?? 'draft')));
$priceRaw = $data['price'] ?? null;
$mediaIn = $data['media'] ?? [];

if ($title === '') {
    api_error('Title is required', 422);
}

if (mb_strlen($title) > 255) {
    api_error('Title is too long', 422);
}

if ($eventDate === '' || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $eventDate)) {
    api_error('Event date is required (YYYY-MM-DD)', 422);
}

$normalizeTime = static function (string $time, string $label): string {
    $time = trim($time);
    if ($time === '') {
        api_error($label . ' is required', 422);
    }
    if (preg_match('/^\d{2}:\d{2}$/', $time)) {
        $time .= ':00';
    }
    if (!preg_match('/^\d{2}:\d{2}:\d{2}$/', $time)) {
        api_error($label . ' must be HH:MM or HH:MM:SS', 422);
    }
    return $time;
};

$startTime = $normalizeTime($startTime, 'Start time');
$endTime = $normalizeTime($endTime, 'End time');

if ($endTime <= $startTime) {
    api_error('End time must be after start time', 422);
}

if (!in_array($type, ['physical', 'online'], true)) {
    api_error('Type must be physical or online', 422);
}

if (!in_array($status, ['draft', 'published'], true)) {
    api_error('Status must be draft or published', 422);
}

$price = null;
if ($priceRaw !== null && $priceRaw !== '') {
    if (!is_numeric($priceRaw)) {
        api_error('Price must be a number', 422);
    }
    $price = round((float) $priceRaw, 2);
}

if ($webinarLink !== '' && !preg_match('#^https?://#i', $webinarLink)) {
    api_error('Webinar link must start with http:// or https://', 422);
}

if (mb_strlen($webinarLink) > 512) {
    api_error('Webinar link is too long', 422);
}

if (mb_strlen($location) > 255) {
    api_error('Location is too long', 422);
}

$normalizePath = static function (string $path): string {
    $path = trim($path);
    if ($path === '') {
        return '';
    }
    if (
        !preg_match('#^(https?:)?//#i', $path)
        && !str_starts_with($path, 'data:')
        && !str_contains($path, '/')
    ) {
        $path = 'uploads/' . ltrim($path, '/');
    }
    return $path;
};

$coverImage = $normalizePath($coverImage);

if (mb_strlen($coverImage) > 512) {
    api_error('Cover image path is too long', 422);
}

$mediaRows = [];
if (!is_array($mediaIn)) {
    api_error('Media must be an array', 422);
}
foreach ($mediaIn as $i => $item) {
    if (!is_array($item)) {
        continue;
    }
    $mediaUrl = $normalizePath(trim((string) ($item['media_url'] ?? '')));
    if ($mediaUrl === '') {
        continue;
    }
    if (mb_strlen($mediaUrl) > 512) {
        api_error('Media URL is too long', 422);
    }
    $mediaType = strtolower(trim((string) ($item['type'] ?? 'image')));
    if (!in_array($mediaType, ['image', 'video'], true)) {
        api_error('Media type must be image or video', 422);
    }
    $mediaRows[] = [
        'type'       => $mediaType,
        'media_url'  => $mediaUrl,
        'sort_order' => (int) ($item['sort_order'] ?? $i),
    ];
}

try {
    $pdo = db();
    events_ensure_schema($pdo);
    $pdo->beginTransaction();

    if ($id > 0) {
        $check = $pdo->prepare(
            'SELECT id, cover_image FROM events WHERE id = ? LIMIT 1'
        );
        $check->execute([$id]);
        $existing = $check->fetch();
        if (!$existing) {
            $pdo->rollBack();
            api_error('Event not found', 404);
        }

        if ($coverImage === '' && !empty($existing['cover_image'])) {
            $coverImage = (string) $existing['cover_image'];
        }

        $stmt = $pdo->prepare(
            'UPDATE events
             SET title = :title,
                 description = :description,
                 cover_image = :cover_image,
                 event_date = :event_date,
                 start_time = :start_time,
                 end_time = :end_time,
                 price = :price,
                 location = :location,
                 type = :type,
                 webinar_link = :webinar_link,
                 status = :status
             WHERE id = :id'
        );
        $stmt->execute([
            ':title'        => $title,
            ':description'  => $description !== '' ? $description : null,
            ':cover_image'  => $coverImage !== '' ? $coverImage : null,
            ':event_date'   => $eventDate,
            ':start_time'   => $startTime,
            ':end_time'     => $endTime,
            ':price'        => $price,
            ':location'     => $location !== '' ? $location : null,
            ':type'         => $type,
            ':webinar_link' => $webinarLink !== '' ? $webinarLink : null,
            ':status'       => $status,
            ':id'           => $id,
        ]);
        $eventId = $id;
    } else {
        $stmt = $pdo->prepare(
            'INSERT INTO events (
                title, description, cover_image, event_date, start_time, end_time,
                price, location, type, webinar_link, status
             ) VALUES (
                :title, :description, :cover_image, :event_date, :start_time, :end_time,
                :price, :location, :type, :webinar_link, :status
             )'
        );
        $stmt->execute([
            ':title'        => $title,
            ':description'  => $description !== '' ? $description : null,
            ':cover_image'  => $coverImage !== '' ? $coverImage : null,
            ':event_date'   => $eventDate,
            ':start_time'   => $startTime,
            ':end_time'     => $endTime,
            ':price'        => $price,
            ':location'     => $location !== '' ? $location : null,
            ':type'         => $type,
            ':webinar_link' => $webinarLink !== '' ? $webinarLink : null,
            ':status'       => $status,
        ]);
        $eventId = (int) $pdo->lastInsertId();
    }

    $pdo->prepare('DELETE FROM event_media WHERE event_id = ?')->execute([$eventId]);

    if ($mediaRows !== []) {
        $insMedia = $pdo->prepare(
            'INSERT INTO event_media (event_id, type, media_url, sort_order)
             VALUES (:event_id, :type, :media_url, :sort_order)'
        );
        foreach ($mediaRows as $row) {
            $insMedia->execute([
                ':event_id'   => $eventId,
                ':type'       => $row['type'],
                ':media_url'  => $row['media_url'],
                ':sort_order' => $row['sort_order'],
            ]);
        }
    }

    $pdo->commit();

    $get = $pdo->prepare(
        'SELECT id, title, description, cover_image, event_date, start_time, end_time,
                price, location, type, webinar_link, status, created_at
         FROM events WHERE id = ? LIMIT 1'
    );
    $get->execute([$eventId]);
    $event = $get->fetch();
    if ($event) {
        $event['id'] = (int) $event['id'];
        $event['price'] = $event['price'] !== null ? (float) $event['price'] : null;

        $mediaStmt = $pdo->prepare(
            'SELECT id, event_id, type, media_url, sort_order, created_at
             FROM event_media
             WHERE event_id = ?
             ORDER BY sort_order ASC, id ASC'
        );
        $mediaStmt->execute([$eventId]);
        $media = $mediaStmt->fetchAll();
        foreach ($media as &$m) {
            $m['id'] = (int) $m['id'];
            $m['event_id'] = (int) $m['event_id'];
            $m['sort_order'] = (int) $m['sort_order'];
        }
        unset($m);
        $event['media'] = $media;
    }

    api_json([
        'ok'    => true,
        'event' => $event,
    ]);
} catch (Throwable $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    api_error('Could not save event', 500);
}
