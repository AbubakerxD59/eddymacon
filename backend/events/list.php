<?php
/**
 * List events for public site and admin.
 * Includes nested media rows ordered by sort_order.
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
    events_ensure_schema($pdo);

    $rowsSql =
        'SELECT id, title, description, cover_image, event_date, start_time, end_time,
                price, location, type, webinar_link, status, created_at
         FROM events';
    $params = [];
    $where = [];

    $status = strtolower(trim((string) ($_GET['status'] ?? '')));
    if ($status === 'published' || $status === 'draft') {
        $where[] = 'status = :status';
        $params[':status'] = $status;
    }

    $upcoming = strtolower(trim((string) ($_GET['upcoming'] ?? '')));
    if ($upcoming === '1' || $upcoming === 'true' || $upcoming === 'yes') {
        $where[] = 'event_date >= CURDATE()';
    }

    if ($where !== []) {
        $rowsSql .= ' WHERE ' . implode(' AND ', $where);
    }

    $rowsSql .= ' ORDER BY event_date ASC, start_time ASC, id ASC';

    if ($params !== []) {
        $stmt = $pdo->prepare($rowsSql);
        $stmt->execute($params);
        $rows = $stmt->fetchAll();
    } else {
        $rows = $pdo->query($rowsSql)->fetchAll();
    }

    $mediaStmt = $pdo->prepare(
        'SELECT id, event_id, type, media_url, sort_order, created_at
         FROM event_media
         WHERE event_id = ?
         ORDER BY sort_order ASC, id ASC'
    );

    foreach ($rows as &$row) {
        $row['id'] = (int) $row['id'];
        $row['price'] = $row['price'] !== null ? (float) $row['price'] : null;

        // Public published list: only expose webinar link for free online events
        if ($status === 'published') {
            $isOnline = strtolower((string) ($row['type'] ?? '')) === 'online';
            $isFree = $row['price'] === null || (float) $row['price'] === 0.0;
            if (!$isOnline || !$isFree) {
                $row['webinar_link'] = null;
            }
        }

        $mediaStmt->execute([(int) $row['id']]);
        $media = $mediaStmt->fetchAll();
        foreach ($media as &$m) {
            $m['id'] = (int) $m['id'];
            $m['event_id'] = (int) $m['event_id'];
            $m['sort_order'] = (int) $m['sort_order'];
        }
        unset($m);
        $row['media'] = $media;
    }
    unset($row);

    api_json([
        'ok'     => true,
        'events' => $rows,
    ]);
} catch (Throwable $e) {
    api_error('Could not load events', 500);
}
