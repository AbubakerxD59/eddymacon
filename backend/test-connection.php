<?php
/**
 * Quick connectivity check: open in browser or run via CLI.
 * Example: php backend/test-connection.php
 *
 * Remove or protect this file on production once verified.
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

require_once __DIR__ . '/db.php';

try {
    $pdo = db();
    $row = $pdo->query('SELECT DATABASE() AS db_name, NOW() AS server_time')->fetch();

    echo json_encode([
        'ok'          => true,
        'message'     => 'MySQL connection successful',
        'database'    => $row['db_name'] ?? null,
        'server_time' => $row['server_time'] ?? null,
    ], JSON_PRETTY_PRINT);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'ok'      => false,
        'message' => 'MySQL connection failed',
        'error'   => $e->getMessage(),
    ], JSON_PRETTY_PRINT);
}
