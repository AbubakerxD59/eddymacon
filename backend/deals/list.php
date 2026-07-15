<?php
/**
 * Admin: list Analyze Deal submissions.
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
    deals_ensure_schema($pdo);

    $rows = $pdo->query(
        'SELECT id, name, phone, email, property_address, asking_price,
                property_type, preferred_exit_strategy, query_text, created_at
         FROM deal_analyses
         ORDER BY created_at DESC, id DESC'
    )->fetchAll();

    api_json([
        'ok'    => true,
        'deals' => $rows,
    ]);
} catch (Throwable $e) {
    api_error('Could not load deal analyses', 500);
}
