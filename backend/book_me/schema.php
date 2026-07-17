<?php
/**
 * Ensure book_me table exists (consultation / book-me requests).
 */

declare(strict_types=1);

function book_me_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS book_me (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(191) NOT NULL,
            email_address VARCHAR(191) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            address VARCHAR(512) NOT NULL,
            booking_date DATE NOT NULL,
            booking_time TIME NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_book_me_created (created_at),
            INDEX idx_book_me_booking (booking_date, booking_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    book_me_migrate_booking_datetime($pdo);
}

function book_me_migrate_booking_datetime(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM book_me LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $dateCol = $pdo->query("SHOW COLUMNS FROM book_me LIKE 'booking_date'")->fetch(PDO::FETCH_ASSOC);
    if (!$dateCol) {
        $pdo->exec(
            "ALTER TABLE book_me
             ADD COLUMN booking_date DATE NULL AFTER address,
             ADD COLUMN booking_time TIME NULL AFTER booking_date"
        );
        // Backfill existing rows so NOT NULL can be applied
        $pdo->exec(
            'UPDATE book_me
             SET booking_date = DATE(created_at),
                 booking_time = TIME(created_at)
             WHERE booking_date IS NULL OR booking_time IS NULL'
        );
        $pdo->exec(
            'ALTER TABLE book_me
             MODIFY COLUMN booking_date DATE NOT NULL,
             MODIFY COLUMN booking_time TIME NOT NULL'
        );
        try {
            $pdo->exec('CREATE INDEX idx_book_me_booking ON book_me (booking_date, booking_time)');
        } catch (Throwable) {
            // index may already exist
        }
    }
}
