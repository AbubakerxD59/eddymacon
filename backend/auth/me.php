<?php
/**
 * GET — whether the current session is an authenticated admin.
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/session.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    api_error('Method not allowed', 405);
}

$authenticated = admin_is_authenticated();

api_json([
    'ok'            => true,
    'authenticated' => $authenticated,
    'email'         => $authenticated ? ($_SESSION['admin_email'] ?? null) : null,
]);
