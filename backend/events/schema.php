<?php
/**
 * Ensure events table exists.
 */

declare(strict_types=1);

function events_ensure_schema(PDO $pdo): void
{
    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS events (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NULL,
            cover_image VARCHAR(512) NULL,
            event_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            price DECIMAL(10, 2) NULL,
            location VARCHAR(255) NULL,
            type ENUM(\'physical\', \'online\') NOT NULL DEFAULT \'physical\',
            webinar_link VARCHAR(512) NULL,
            status ENUM(\'draft\', \'published\') NOT NULL DEFAULT \'draft\',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_events_date (event_date),
            INDEX idx_events_type (type),
            INDEX idx_events_status (status),
            INDEX idx_events_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS event_media (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            event_id INT UNSIGNED NOT NULL,
            type ENUM(\'image\', \'video\') NOT NULL DEFAULT \'image\',
            media_url VARCHAR(512) NOT NULL,
            sort_order INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_event_media_event (event_id),
            INDEX idx_event_media_sort (event_id, sort_order),
            CONSTRAINT fk_event_media_event
                FOREIGN KEY (event_id) REFERENCES events (id)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS event_bookings (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            event_id INT UNSIGNED NOT NULL,
            customer_name VARCHAR(191) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            email_address VARCHAR(191) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_event_bookings_event (event_id),
            INDEX idx_event_bookings_created (created_at),
            CONSTRAINT fk_event_bookings_event
                FOREIGN KEY (event_id) REFERENCES events (id)
                ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'
    );

    events_migrate_event_media_schema($pdo);
    events_migrate_events_time_columns($pdo);
    events_migrate_drop_thumbnail($pdo);
    events_migrate_events_status($pdo);
    events_migrate_bookings_optional_email($pdo);
}

function events_migrate_bookings_optional_email(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM event_bookings LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $col = $pdo->query("SHOW COLUMNS FROM event_bookings LIKE 'email_address'")->fetch(PDO::FETCH_ASSOC);
    if (!$col) {
        return;
    }

    if (strtoupper((string) ($col['Null'] ?? '')) === 'NO') {
        $pdo->exec('ALTER TABLE event_bookings MODIFY COLUMN email_address VARCHAR(191) NULL');
    }
}

function events_migrate_events_status(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM events LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $columns = array_column(
        $pdo->query('SHOW COLUMNS FROM events')->fetchAll(PDO::FETCH_ASSOC),
        'Field'
    );

    if (!in_array('status', $columns, true)) {
        $pdo->exec(
            "ALTER TABLE events
             ADD COLUMN status ENUM('draft', 'published') NOT NULL DEFAULT 'draft' AFTER webinar_link,
             ADD INDEX idx_events_status (status)"
        );
    }
}

function events_migrate_drop_thumbnail(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM events LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $columns = array_column(
        $pdo->query('SHOW COLUMNS FROM events')->fetchAll(PDO::FETCH_ASSOC),
        'Field'
    );

    if (in_array('thumbnail', $columns, true)) {
        $pdo->exec('ALTER TABLE events DROP COLUMN thumbnail');
    }
}

function events_migrate_events_time_columns(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM events LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $columns = array_column(
        $pdo->query('SHOW COLUMNS FROM events')->fetchAll(PDO::FETCH_ASSOC),
        'Field'
    );
    $has = static fn(string $col): bool => in_array($col, $columns, true);

    if (!$has('start_time')) {
        $pdo->exec('ALTER TABLE events ADD COLUMN start_time TIME NULL AFTER event_date');
    }
    if (!$has('end_time')) {
        $pdo->exec('ALTER TABLE events ADD COLUMN end_time TIME NULL AFTER start_time');
    }

    // Refresh column list after possible ADDs
    $columns = array_column(
        $pdo->query('SHOW COLUMNS FROM events')->fetchAll(PDO::FETCH_ASSOC),
        'Field'
    );
    $has = static fn(string $col): bool => in_array($col, $columns, true);

    if ($has('event_time') && $has('start_time')) {
        $pdo->exec(
            'UPDATE events
             SET start_time = COALESCE(start_time, event_time),
                 end_time = COALESCE(end_time, event_time)
             WHERE start_time IS NULL OR end_time IS NULL'
        );
        $pdo->exec('ALTER TABLE events DROP COLUMN event_time');
    }

    // Enforce NOT NULL after backfill (new installs already have NOT NULL)
    $pdo->exec("UPDATE events SET start_time = '00:00:00' WHERE start_time IS NULL");
    $pdo->exec("UPDATE events SET end_time = '00:00:00' WHERE end_time IS NULL");

    $colMeta = $pdo->query('SHOW COLUMNS FROM events LIKE \'start_time\'')->fetch(PDO::FETCH_ASSOC);
    if ($colMeta && strtoupper((string) ($colMeta['Null'] ?? '')) === 'YES') {
        $pdo->exec('ALTER TABLE events MODIFY COLUMN start_time TIME NOT NULL');
    }
    $colMeta = $pdo->query('SHOW COLUMNS FROM events LIKE \'end_time\'')->fetch(PDO::FETCH_ASSOC);
    if ($colMeta && strtoupper((string) ($colMeta['Null'] ?? '')) === 'YES') {
        $pdo->exec('ALTER TABLE events MODIFY COLUMN end_time TIME NOT NULL');
    }
}

function events_migrate_event_media_schema(PDO $pdo): void
{
    try {
        $pdo->query('SELECT 1 FROM event_media LIMIT 1');
    } catch (Throwable) {
        return;
    }

    $columns = array_column(
        $pdo->query('SHOW COLUMNS FROM event_media')->fetchAll(PDO::FETCH_ASSOC),
        'Field'
    );
    $has = static fn(string $col): bool => in_array($col, $columns, true);

    if ($has('image') && !$has('media_url')) {
        $pdo->exec('ALTER TABLE event_media CHANGE COLUMN image media_url VARCHAR(512) NOT NULL');
    } elseif ($has('image') && $has('media_url')) {
        $pdo->exec('ALTER TABLE event_media DROP COLUMN image');
    }

    if (!$has('type')) {
        $pdo->exec(
            "ALTER TABLE event_media ADD COLUMN type ENUM('image', 'video') NOT NULL DEFAULT 'image' AFTER event_id"
        );
    }
}
