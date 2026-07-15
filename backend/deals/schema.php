<?php
/**
 * Ensure deal analyses (Analyze Deal) table exists.
 */

declare(strict_types=1);

function deals_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS deal_analyses (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(191) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            email VARCHAR(191) NOT NULL,
            property_address VARCHAR(255) NOT NULL,
            asking_price VARCHAR(100) NOT NULL,
            property_type VARCHAR(50) NOT NULL,
            preferred_exit_strategy VARCHAR(50) NOT NULL,
            query_text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_deal_analyses_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );
}
