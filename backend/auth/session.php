<?php
/**
 * Admin session helpers.
 */

declare(strict_types=1);

function admin_session_start(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }

    session_name('eddymacon_admin');
    session_set_cookie_params([
        'lifetime' => 0,
        'path'     => '/',
        'secure'   => (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off'),
        'httponly'  => true,
        'samesite' => 'Lax',
    ]);
    session_start();
}

function admin_is_authenticated(): bool
{
    admin_session_start();
    return !empty($_SESSION['admin_authenticated']) && $_SESSION['admin_authenticated'] === true;
}

function admin_login(string $email): void
{
    admin_session_start();
    session_regenerate_id(true);
    $_SESSION['admin_authenticated'] = true;
    $_SESSION['admin_email'] = $email;
    $_SESSION['admin_login_at'] = time();
}

function admin_logout(): void
{
    admin_session_start();
    $_SESSION = [];

    if (ini_get('session.use_cookies')) {
        $params = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $params['path'], $params['domain'] ?? '', (bool) $params['secure'], (bool) $params['httponly']);
    }

    session_destroy();
}
