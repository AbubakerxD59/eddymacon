<?php
/**
 * Authenticated image upload for site content.
 * POST multipart: file
 */

declare(strict_types=1);

require_once __DIR__ . '/../helpers.php';
require_once __DIR__ . '/../auth/session.php';

api_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_error('Method not allowed', 405);
}

if (!admin_is_authenticated()) {
    api_error('Unauthorized', 401);
}

if (!isset($_FILES['file']) || !is_array($_FILES['file'])) {
    api_error('No file uploaded', 422);
}

$file = $_FILES['file'];

if (($file['error'] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) {
    api_error('Upload failed', 400, ['code' => $file['error'] ?? null]);
}

$maxBytes = 5 * 1024 * 1024;
if (($file['size'] ?? 0) <= 0 || $file['size'] > $maxBytes) {
    api_error('File must be between 1 byte and 5MB', 422);
}

$finfo = new finfo(FILEINFO_MIME_TYPE);
$mime = $finfo->file($file['tmp_name']) ?: '';

$allowed = [
    'image/jpeg' => 'jpg',
    'image/png'  => 'png',
    'image/webp' => 'webp',
    'image/gif'  => 'gif',
];

if (!isset($allowed[$mime])) {
    api_error('Only JPEG, PNG, WebP, or GIF images are allowed', 422);
}

$ext = $allowed[$mime];
$basename = 'img_' . date('Ymd_His') . '_' . bin2hex(random_bytes(4)) . '.' . $ext;

$uploadsDir = dirname(__DIR__, 2) . '/uploads';
if (!is_dir($uploadsDir) && !mkdir($uploadsDir, 0755, true)) {
    api_error('Could not create uploads directory', 500);
}

$dest = $uploadsDir . '/' . $basename;
if (!move_uploaded_file($file['tmp_name'], $dest)) {
    api_error('Failed to save uploaded file', 500);
}

@chmod($dest, 0644);

$path = 'uploads/' . $basename;

api_json([
    'ok'       => true,
    'path'     => $path,
    'filename' => $basename,
    'mime'     => $mime,
    'size'     => (int) $file['size'],
]);
