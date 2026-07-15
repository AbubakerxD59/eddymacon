<?php
/**
 * End admin session (POST preferred; GET allowed for simple links).
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/session.php';

api_headers();

if (!in_array($_SERVER['REQUEST_METHOD'], ['POST', 'GET'], true)) {
    api_error('Method not allowed', 405);
}

admin_logout();

api_json(['ok' => true]);
