<?php
/**
 * PDO MySQL connection helper.
 *
 * Usage:
 *   require_once __DIR__ . '/db.php';
 *   $pdo = db();
 */

declare(strict_types=1);

function db(): PDO
{
    static $pdo = null;

    if ($pdo instanceof PDO) {
        return $pdo;
    }

    $configPath = __DIR__ . '/config/database.php';
    if (!is_file($configPath)) {
        throw new RuntimeException(
            'Missing backend/config/database.php — copy database.example.php and set credentials.'
        );
    }

    /** @var array{host:string,port:int,dbname:string,username:string,password:string,charset:string} $config */
    $config = require $configPath;

    $dsn = sprintf(
        'mysql:host=%s;port=%d;dbname=%s;charset=%s',
        $config['host'],
        (int) $config['port'],
        $config['dbname'],
        $config['charset']
    );

    $pdo = new PDO($dsn, $config['username'], $config['password'], [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);

    return $pdo;
}
