<?php
/**
 * Simple .env file loader
 * Loads environment variables from .env file
 */

function loadEnv($path = '/var/secrets/kidsevents.env') {
    if (!file_exists($path)) {
        // Fallback to project directory .env for backwards compatibility
        $fallback = __DIR__ . '/.env';
        if (file_exists($fallback)) {
            $path = $fallback;
        } else {
            return false;
        }
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

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

            // Remove quotes if present
            if (preg_match('/^(["\'])(.*)\\1$/', $value, $matches)) {
                $value = $matches[2];
            }

            // Set environment variable and $_ENV
            putenv("$key=$value");
            $_ENV[$key] = $value;
            $_SERVER[$key] = $value;
        }
    }

    return true;
}

// Auto-load .env file
loadEnv();
?>
