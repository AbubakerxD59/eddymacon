<?php
/**
 * Ensure books table exists (admin-managed titles + sale links).
 */

declare(strict_types=1);

function books_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS books (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            sale_url VARCHAR(512) NOT NULL,
            cover_image VARCHAR(512) NULL,
            is_featured TINYINT(1) NOT NULL DEFAULT 0,
            sort_order INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_books_featured (is_featured),
            INDEX idx_books_sort (sort_order, id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    $count = (int) $pdo->query('SELECT COUNT(*) FROM books')->fetchColumn();
    if ($count > 0) {
        return;
    }

    $ins = $pdo->prepare(
        'INSERT INTO books (title, description, sale_url, is_featured, sort_order)
         VALUES (:title, :description, :sale_url, 1, 0)'
    );
    $ins->execute([
        ':title'       => 'From Bid to Build',
        ':description' => 'Practical real estate education from analysis to execution.',
        ':sale_url'    => 'https://a.co/d/9GrX6ir',
    ]);
}
