<?php
/**
 * Weekend-picks email signup for Toronto Kids Events.
 *
 *   POST  subscribe.php            email=&age=&website=(honeypot)   -> JSON {ok:true}
 *   GET   subscribe.php?a=unsub&e=<email>&t=<hmac>                  -> one-click unsubscribe page
 *
 * Storage: data/subscribers.json (denied by data/.htaccess, gitignored).
 * Tokens are HMAC-SHA256(email) with a secret generated on first use in data/.secret.
 */

declare(strict_types=1);

const DATA_DIR = __DIR__ . '/data';
const STORE = DATA_DIR . '/subscribers.json';
const RL_DIR = DATA_DIR . '/rl';
const AGES = ['', 'babies', 'toddlers', 'kids'];

function secret(): string {
    $f = DATA_DIR . '/.secret';
    if (!is_file($f)) {
        file_put_contents($f, bin2hex(random_bytes(32)), LOCK_EX);
        @chmod($f, 0660);
    }
    return trim((string) file_get_contents($f));
}

function token(string $email): string {
    return hash_hmac('sha256', strtolower($email), secret());
}

function out(array $body, int $code = 200): never {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($body);
    exit;
}

function with_store(callable $fn): mixed {
    $fh = fopen(STORE, 'c+');
    @chmod(STORE, 0660); // group-writable so the cron/digest user (john, in www-data) can manage it
    if (!$fh) {
        out(['ok' => false, 'error' => 'Storage unavailable. Please try again later.'], 500);
    }
    flock($fh, LOCK_EX);
    $raw = stream_get_contents($fh);
    $db = $raw ? (json_decode($raw, true) ?: []) : [];
    $res = $fn($db);
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, json_encode($db, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
    fflush($fh);
    flock($fh, LOCK_UN);
    fclose($fh);
    return $res;
}

function rate_limited(): bool {
    if (!is_dir(RL_DIR)) {
        @mkdir(RL_DIR, 02770, true);
        @chmod(RL_DIR, 02770);
    }
    $ip = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? 'x';
    $f = RL_DIR . '/' . hash('sha256', $ip . secret());
    $hits = [];
    if (is_file($f)) {
        $hits = array_filter(array_map('intval', explode(',', (string) file_get_contents($f))), fn($t) => $t > time() - 3600);
    }
    if (count($hits) >= 6) {
        return true;
    }
    $hits[] = time();
    file_put_contents($f, implode(',', $hits), LOCK_EX);
    @chmod($f, 0660);
    return false;
}

if (!is_dir(DATA_DIR)) {
    out(['ok' => false, 'error' => 'Not configured.'], 500);
}

// ---- unsubscribe (GET link from every email) ----
if (($_GET['a'] ?? '') === 'unsub') {
    $email = strtolower(trim((string) ($_GET['e'] ?? '')));
    $ok = $email !== '' && hash_equals(token($email), (string) ($_GET['t'] ?? ''));
    if ($ok) {
        with_store(function (&$db) use ($email) {
            if (isset($db[$email])) {
                $db[$email]['status'] = 'unsubscribed';
                $db[$email]['unsubscribed_at'] = gmdate('c');
            }
        });
    }
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: no-store');
    $msg = $ok ? "You're unsubscribed. No more weekend-picks emails." : 'That unsubscribe link is not valid. Reply to any email and we will remove you by hand.';
    echo '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Unsubscribe</title>'
       . '<body style="font:18px/1.5 system-ui,sans-serif;max-width:32rem;margin:15vh auto;padding:0 20px;color:#1F2937"><h1 style="color:#4F46E5">Toronto Kids Events</h1><p>'
       . htmlspecialchars($msg) . '</p><p><a href="/kidsevents/" style="color:#4F46E5">Back to the calendar</a></p></body>';
    exit;
}

// ---- subscribe (POST from the calendar page) ----
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    out(['ok' => false, 'error' => 'POST only.'], 405);
}
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && parse_url($origin, PHP_URL_HOST) !== ($_SERVER['HTTP_HOST'] ?? '')) {
    out(['ok' => false, 'error' => 'Bad origin.'], 403);
}
if (trim((string) ($_POST['website'] ?? '')) !== '') {
    out(['ok' => true]); // honeypot: pretend success
}
if (rate_limited()) {
    out(['ok' => false, 'error' => 'Too many attempts. Please try again in an hour.'], 429);
}
$email = strtolower(trim((string) ($_POST['email'] ?? '')));
if (strlen($email) > 254 || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    out(['ok' => false, 'error' => 'Please enter a valid email address.'], 422);
}
$age = (string) ($_POST['age'] ?? '');
if (!in_array($age, AGES, true)) {
    $age = '';
}

with_store(function (&$db) use ($email, $age) {
    $prev = $db[$email] ?? null;
    $db[$email] = [
        'status' => 'subscribed',
        'age' => $age,
        'source' => substr(preg_replace('/[^a-z0-9_-]/i', '', (string) ($_POST['src'] ?? '')), 0, 24),
        'subscribed_at' => $prev['subscribed_at'] ?? gmdate('c'),
        'consent' => 'express: submitted signup form (' . gmdate('c') . ')',
    ];
});
out(['ok' => true]);
