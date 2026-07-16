<?php
/**
 * Public: submit Analyze Deal form.
 * POST JSON: name, phone, email, property_address, asking_price,
 *            property_type, preferred_exit_strategy, query
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../db.php';
require_once __DIR__ . '/schema.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_error('Method not allowed', 405);
}

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

$name = trim((string) ($data['name'] ?? ''));
$phone = trim((string) ($data['phone'] ?? ''));
$email = trim((string) ($data['email'] ?? ''));
$propertyAddress = trim((string) ($data['property_address'] ?? ''));
$askingPrice = trim((string) ($data['asking_price'] ?? ''));
$propertyType = trim((string) ($data['property_type'] ?? ''));
$exitStrategy = trim((string) ($data['preferred_exit_strategy'] ?? ''));
$query = trim((string) ($data['query'] ?? ''));

$allowedTypes = ['single_family', 'multi_family', 'commercial', 'land'];
$allowedExits = ['flip', 'rental', 'wholesale', 'brrrr', 'others'];

if (
    $name === '' || $phone === '' || $email === '' || $propertyAddress === ''
    || $askingPrice === '' || $propertyType === '' || $exitStrategy === '' || $query === ''
) {
    api_error('All fields are required', 422);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    api_error('Please enter a valid email address', 422);
}

if (!in_array($propertyType, $allowedTypes, true)) {
    api_error('Invalid property type', 422);
}

if (!in_array($exitStrategy, $allowedExits, true)) {
    api_error('Invalid preferred exit strategy', 422);
}

if (
    mb_strlen($name) > 191
    || mb_strlen($email) > 191
    || mb_strlen($phone) > 50
    || mb_strlen($propertyAddress) > 255
    || mb_strlen($askingPrice) > 100
) {
    api_error('One or more fields are too long', 422);
}

try {
    $pdo = db();
    deals_ensure_schema($pdo);

    $stmt = $pdo->prepare(
        'INSERT INTO deal_analyses
            (name, phone, email, property_address, asking_price, property_type, preferred_exit_strategy, query_text)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    );
    $stmt->execute([
        $name,
        $phone,
        $email,
        $propertyAddress,
        $askingPrice,
        $propertyType,
        $exitStrategy,
        $query,
    ]);

    api_json([
        'ok' => true,
        'id' => (int) $pdo->lastInsertId(),
    ]);
} catch (Throwable $e) {
    api_error('Could not save deal analysis', 500);
}
