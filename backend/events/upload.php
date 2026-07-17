<?php
/**
 * Admin: upload event media (image or video).
 * POST multipart: file
 * Images: jpeg/png/webp/gif, max 2MB
 * Videos: mp4/webm/mov, max 10MB
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

$finfo = new finfo(FILEINFO_MIME_TYPE);
$mime = $finfo->file($file['tmp_name']) ?: '';

$imageAllowed = [
    'image/jpeg' => 'jpg',
    'image/png'  => 'png',
    'image/webp' => 'webp',
    'image/gif'  => 'gif',
];

$videoAllowed = [
    'video/mp4'       => 'mp4',
    'video/webm'      => 'webm',
    'video/quicktime' => 'mov',
];

$mediaType = null;
$maxBytes = 0;
$prefix = 'media_';

if (isset($imageAllowed[$mime])) {
    $mediaType = 'image';
    $maxBytes = 2 * 1024 * 1024;
    $ext = $imageAllowed[$mime];
    $prefix = 'img_';
} elseif (isset($videoAllowed[$mime])) {
    $mediaType = 'video';
    $maxBytes = 10 * 1024 * 1024;
    $ext = $videoAllowed[$mime];
    $prefix = 'vid_';
} else {
    api_error('Only JPEG, PNG, WebP, GIF images or MP4, WebM, MOV videos are allowed', 422);
}

$size = (int) ($file['size'] ?? 0);
if ($size <= 0 || $size > $maxBytes) {
    $limitLabel = $mediaType === 'image' ? '2MB' : '10MB';
    api_error(
        ucfirst($mediaType) . ' must be between 1 byte and ' . $limitLabel,
        422
    );
}

$basename = $prefix . date('Ymd_His') . '_' . bin2hex(random_bytes(4)) . '.' . $ext;

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
    'ok'         => true,
    'path'       => $path,
    'filename'   => $basename,
    'mime'       => $mime,
    'size'       => $size,
    'media_type' => $mediaType,
]);
