<?php
/**
 * Secure Configuration Loader
 * Loads environment variables from .env file or system environment
 */

// Prevent direct access
if (!defined('CONFIG_LOADED')) {
    define('CONFIG_LOADED', true);
}

/**
 * Load environment variables from .env file
 */
function loadEnv($filePath = '.env') {
    if (!file_exists($filePath)) {
        return false;
    }

    $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        // Skip comments
        if (strpos(trim($line), '#') === 0) {
            continue;
        }

        // Parse KEY=VALUE
        if (strpos($line, '=') !== false) {
            list($key, $value) = explode('=', $line, 2);
            $key = trim($key);
            $value = trim($value);

            // Set environment variable if not already set
            if (!getenv($key)) {
                putenv("$key=$value");
                $_ENV[$key] = $value;
                $_SERVER[$key] = $value;
            }
        }
    }

    return true;
}

/**
 * Get environment variable with fallback
 */
function env($key, $default = null) {
    $value = getenv($key);
    if ($value === false) {
        return $default;
    }
    return $value;
}

/**
 * Simple rate limiter using file-based storage
 */
class RateLimiter {
    private $storageDir;
    private $maxRequests;
    private $windowHours;

    public function __construct($storageDir = '/tmp/rate_limits') {
        $this->storageDir = $storageDir;
        $this->maxRequests = (int)env('RATE_LIMIT_MAX_REQUESTS', 100);
        $this->windowHours = (int)env('RATE_LIMIT_WINDOW_HOURS', 1);

        if (!is_dir($this->storageDir)) {
            @mkdir($this->storageDir, 0755, true);
        }
    }

    public function checkLimit($identifier) {
        $hash = md5($identifier);
        $file = $this->storageDir . '/' . $hash;

        $now = time();
        $windowStart = $now - ($this->windowHours * 3600);

        // Load existing requests
        $requests = [];
        if (file_exists($file)) {
            $data = file_get_contents($file);
            $requests = json_decode($data, true) ?: [];
        }

        // Remove old requests outside the window
        $requests = array_filter($requests, function($timestamp) use ($windowStart) {
            return $timestamp > $windowStart;
        });

        // Check if limit exceeded
        if (count($requests) >= $this->maxRequests) {
            return false;
        }

        // Add current request
        $requests[] = $now;

        // Save updated requests
        file_put_contents($file, json_encode($requests));

        return true;
    }

    public function getRemainingRequests($identifier) {
        $hash = md5($identifier);
        $file = $this->storageDir . '/' . $hash;

        if (!file_exists($file)) {
            return $this->maxRequests;
        }

        $now = time();
        $windowStart = $now - ($this->windowHours * 3600);

        $data = file_get_contents($file);
        $requests = json_decode($data, true) ?: [];

        $requests = array_filter($requests, function($timestamp) use ($windowStart) {
            return $timestamp > $windowStart;
        });

        return max(0, $this->maxRequests - count($requests));
    }
}

/**
 * Validate and sanitize input
 */
function sanitizeInput($input, $maxLength = 500) {
    if (empty($input)) {
        return '';
    }

    // Remove null bytes
    $input = str_replace("\0", '', $input);

    // Limit length
    $input = substr($input, 0, $maxLength);

    // Remove control characters except newlines
    $input = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $input);

    return trim($input);
}

/**
 * Validate referer to prevent unauthorized proxy usage
 */
function validateReferer() {
    $allowedReferer = env('ALLOWED_REFERER', null);

    // If no referer restriction is set, skip validation
    if ($allowedReferer === null || $allowedReferer === '*') {
        return true;
    }

    $referer = $_SERVER['HTTP_REFERER'] ?? '';

    if (empty($referer)) {
        // You can choose to allow or deny empty referers
        // For strict security, deny empty referers:
        if (env('REQUIRE_REFERER', 'false') === 'true') {
            return false;
        }
        return true;
    }

    // Check if referer matches allowed domain
    $refererHost = parse_url($referer, PHP_URL_HOST);
    $allowedHost = parse_url($allowedReferer, PHP_URL_HOST);

    if ($allowedHost === null) {
        $allowedHost = $allowedReferer;
    }

    return $refererHost === $allowedHost;
}

/**
 * Set secure headers
 */
function setSecurityHeaders($allowedOrigin = null) {
    // CORS headers
    if ($allowedOrigin === null) {
        $allowedOrigin = env('ALLOWED_ORIGIN', '*');
    }

    header('Access-Control-Allow-Origin: ' . $allowedOrigin);
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');
    header('Access-Control-Max-Age: 3600');

    // Security headers
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');

    // Content type
    header('Content-Type: application/json; charset=utf-8');
}

/**
 * Send JSON error response
 */
function sendError($message, $code = 400, $includeDetails = false) {
    http_response_code($code);

    $response = ['error' => $message];

    // Only include details in development mode
    if ($includeDetails && env('APP_ENV') === 'development') {
        $response['details'] = $includeDetails;
    }

    echo json_encode($response);
    exit;
}

/**
 * Send JSON success response
 */
function sendSuccess($data) {
    http_response_code(200);
    echo json_encode($data);
    exit;
}

// Load environment variables from secure location
loadEnv('/var/secrets/kidsevents.env');

// Verify API key is configured
if (!env('GOOGLE_API_KEY')) {
    error_log('GOOGLE_API_KEY not configured in environment');
}
?>
