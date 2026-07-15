<?php
/**
 * POST JSON { email, password } → start admin session.
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/session.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_error('Method not allowed', 405);
}

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

$email = strtolower(trim((string) ($data['email'] ?? '')));
$password = (string) ($data['password'] ?? '');

if ($email === '' || $password === '') {
    api_error('Email and password are required', 422);
}

$configPath = __DIR__ . '/../config/auth.php';
if (!is_file($configPath)) {
    api_error('Auth is not configured', 500);
}

/** @var array{email:string,password_hash:string} $auth */
$auth = require $configPath;

$ok = hash_equals(strtolower($auth['email']), $email)
    && password_verify($password, $auth['password_hash']);

if (!$ok) {
    // Constant-ish timing for failed password_verify path
    password_verify($password, '$2y$10$abcdefghijklmnopqrstuuABCDEFGHIJKLMNOPQRSTUVWX12');
    api_error('Invalid email or password', 401);
}

admin_login($email);

api_json([
    'ok'    => true,
    'email' => $email,
]);
