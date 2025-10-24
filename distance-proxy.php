<?php
/**
 * Google Distance Matrix API Proxy
 * Secure proxy that calculates actual road/walking distances
 */

require_once __DIR__ . '/config.php';

// Set security headers
setSecurityHeaders();

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// Validate referer (optional - prevents direct access from other domains)
if (!validateReferer()) {
    error_log('Invalid referer: ' . ($_SERVER['HTTP_REFERER'] ?? 'none'));
    sendError('Access denied', 403);
}

// Rate limiting
$rateLimiter = new RateLimiter();
$clientIp = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

if (!$rateLimiter->checkLimit($clientIp)) {
    sendError('Rate limit exceeded. Please try again later.', 429);
}

// Get API key from environment
$apiKey = env('GOOGLE_MAPS_API_KEY');
if (empty($apiKey)) {
    error_log('Google Maps API key not configured');
    sendError('Service configuration error', 500);
}

// Get and validate parameters
$origins = isset($_GET['origins']) ? sanitizeInput($_GET['origins'], 100) : '';
$destinations = isset($_GET['destinations']) ? sanitizeInput($_GET['destinations'], 100) : '';

if (empty($origins) || empty($destinations)) {
    sendError('Missing origins or destinations', 400);
}

// Validate lat/lng format to prevent SSRF attacks
// Expected format: "lat,lng" where lat and lng are decimal numbers
$coordPattern = '/^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/';

if (!preg_match($coordPattern, $origins)) {
    sendError('Invalid origins coordinate format. Expected: "lat,lng"', 400);
}

if (!preg_match($coordPattern, $destinations)) {
    sendError('Invalid destinations coordinate format. Expected: "lat,lng"', 400);
}

// Additional validation: ensure coordinates are within valid ranges
list($origLat, $origLng) = explode(',', $origins);
list($destLat, $destLng) = explode(',', $destinations);

// Validate latitude range
if (abs($origLat) > 90 || abs($destLat) > 90) {
    sendError('Invalid latitude. Must be between -90 and 90.', 400);
}

// Validate longitude range
if (abs($origLng) > 180 || abs($destLng) > 180) {
    sendError('Invalid longitude. Must be between -180 and 180.', 400);
}

// Optional: Restrict to Toronto area for extra security
// Uncomment to enable Toronto-only restriction
/*
$torontoLatMin = 43.4;
$torontoLatMax = 43.9;
$torontoLngMin = -79.8;
$torontoLngMax = -79.1;

if ($origLat < $torontoLatMin || $origLat > $torontoLatMax ||
    $destLat < $torontoLatMin || $destLat > $torontoLatMax ||
    $origLng < $torontoLngMin || $origLng > $torontoLngMax ||
    $destLng < $torontoLngMin || $destLng > $torontoLngMax) {
    sendError('Locations must be within Toronto area', 400);
}
*/

// Try new Routes API first, fallback to legacy Distance Matrix API
// Build Google Distance Matrix API URL (legacy but still works)
$url = 'https://maps.googleapis.com/maps/api/distancematrix/json?' . http_build_query([
    'origins' => $origins,
    'destinations' => $destinations,
    'mode' => 'walking',
    'units' => 'metric',
    'key' => $apiKey
]);

// Use cURL for better control and error handling
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false); // Prevent SSRF via redirects

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if (curl_errno($ch)) {
    $errorMsg = curl_error($ch);
    curl_close($ch);
    error_log("Google Distance Matrix API cURL error: $errorMsg");
    sendError('Unable to complete request', 502);
}

curl_close($ch);

if ($httpCode !== 200) {
    error_log("Google Distance Matrix API error: HTTP $httpCode - Response: $response");
    sendError('Service temporarily unavailable', 503);
}

// Validate response is valid JSON
$data = json_decode($response, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    error_log("Invalid JSON response from Google Distance Matrix API");
    sendError('Invalid response from service', 502);
}

// Check API response status
$status = $data['status'] ?? 'UNKNOWN';
if ($status !== 'OK') {
    error_log("Google Distance Matrix API status: $status");
    sendError('Unable to calculate distance', 400);
}

// Return the response
sendSuccess($data);
?>
