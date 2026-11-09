#!/usr/bin/env python3
"""Weekly "weekend picks" email for Toronto Kids Events.

Safe by default: with no flags it only writes a preview (data/digest_preview.html)
and prints a summary. Nothing is sent until you pass --send.

  python3 weekly_digest.py                      # preview only
  python3 weekly_digest.py --send --to me@x.com # send one test copy to a single address
  python3 weekly_digest.py --send               # send to every active subscriber

Sender/transport (env): KE_MAIL_FROM, KE_SMTP_HOST (default localhost), KE_SMTP_PORT (25),
KE_SMTP_USER / KE_SMTP_PASS (optional, enables STARTTLS + login).
Every message carries a per-recipient unsubscribe link and List-Unsubscribe headers.
"""
import argparse
import hashlib
import hmac
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from urllib.parse import quote

import ke_curate as kc

SITE = 'https://joshuaopolko.com/kidsevents/'
DATA = kc.ROOT / 'data'
DAYN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def fmt_t(t):
    h, m = int(t[:2]), t[3:5]
    ap = 'PM' if h >= 12 else 'AM'
    h = h % 12 or 12
    return f"{h}{'' if m == '00' else ':' + m} {ap}"


def day_label(d):
    return f'{DAYN[d.weekday()][:3]} {MONN[d.month - 1]} {d.day}'


def picks_for(events, age, limit=8):
    days = [d.isoformat() for d in kc.weekend_days()]
    pool = [e for e in kc.curated(events, age) if e['date'] in days]
    score = kc.scorer(events, age)
    pool.sort(key=lambda e: -score(e))
    seen, out = {}, []
    for e in pool:
        sk = (e['title'], kc.venue(e), e['start_time'])
        if sk in seen:
            seen[sk]['days'].append(e['date'])
            continue
        seen[sk] = {'e': e, 'days': [e['date']]}
        out.append(seen[sk])
    return out[:limit], len(pool), days


def unsub_url(email):
    secret = (DATA / '.secret').read_text(encoding='utf-8').strip()
    t = hmac.new(secret.encode(), email.lower().encode(), hashlib.sha256).hexdigest()
    return f'{SITE}subscribe.php?a=unsub&e={quote(email)}&t={t}'


def render(items, total, days, age, unsub):
    from datetime import date
    ds = [date.fromisoformat(d) for d in days]
    rng = day_label(ds[0]) + (' – ' + day_label(ds[-1]) if len(ds) > 1 else '')
    subject = f'Weekend picks for Toronto kids · {rng}'
    text = [f'This weekend in Toronto ({rng}) — {total} things on.', '']
    rows = []
    for it in items:
        e, dys = it['e'], it['days']
        when = ' & '.join(DAYN[date.fromisoformat(d).weekday()][:3] for d in dys) + ' · ' + fmt_t(e['start_time'])
        where = kc.venue(e) + ((' · ' + e['venue']['neighborhood']) if (e.get('venue') or {}).get('neighborhood') else '')
        link = e.get('website') or f"{SITE}#d={e['date']}&e={quote(e.get('id', ''))}"
        free = ' · Free' if kc.is_free(e) else ''
        text += [f"- {e['title']} ({when}{free})", f'  {where}', f'  {link}', '']
        rows.append(
            f'<tr><td style="padding:12px 0;border-bottom:1px solid #EEF0FB">'
            f'<div style="font:700 12px system-ui;color:#DB2777;text-transform:uppercase;letter-spacing:.05em">{escape(when)}{escape(free)}</div>'
            f'<a href="{escape(link)}" style="font:800 17px/1.3 system-ui;color:#1F2937;text-decoration:none">{escape(e["title"])}</a>'
            f'<div style="font:600 14px system-ui;color:#6B7280">{escape(where)}</div></td></tr>')
    text += [f'See everything, filter by age, add to your calendar: {SITE}', '', f'Unsubscribe: {unsub}']
    html = (f'<!doctype html><html><body style="margin:0;background:#F5F3FF;padding:20px"><table role="presentation" width="100%" style="max-width:560px;margin:0 auto;background:#fff;border-radius:16px;padding:22px">'
            f'<tr><td><h1 style="font:900 22px system-ui;color:#4F46E5;margin:0 0 4px">☀️ This weekend with the kids</h1>'
            f'<p style="font:600 14px system-ui;color:#6B7280;margin:0 0 8px">{escape(rng)} · {total} things on, our top picks below</p></td></tr>'
            + ''.join(rows) +
            f'<tr><td style="padding-top:18px"><a href="{SITE}" style="display:inline-block;background:#6366F1;color:#fff;font:800 15px system-ui;padding:12px 20px;border-radius:12px;text-decoration:none">See the full calendar</a></td></tr>'
            f'<tr><td style="padding-top:22px;font:12px system-ui;color:#9CA3AF">You are getting this because you signed up at joshuaopolko.com/kidsevents. '
            f'<a href="{escape(unsub)}" style="color:#9CA3AF">Unsubscribe</a></td></tr></table></body></html>')
    return subject, '\n'.join(text), html


def send(smtp, sender, to, subject, text, html, unsub):
    m = EmailMessage()
    m['Subject'], m['From'], m['To'] = subject, sender, to
    m['List-Unsubscribe'] = f'<{unsub}>'
    m['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    m.set_content(text)
    m.add_alternative(html, subtype='html')
    smtp.send_message(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--send', action='store_true', help='actually send (default: preview only)')
    ap.add_argument('--to', help='send only to this address (test)')
    a = ap.parse_args()

    events = kc.load_events()
    subs_path = DATA / 'subscribers.json'
    subs = json.loads(subs_path.read_text(encoding='utf-8')) if subs_path.exists() else {}
    active = {e: s for e, s in subs.items() if s.get('status') == 'subscribed'}

    items, total, days = picks_for(events, None)
    subject, text, html = render(items, total, days, None, '#unsubscribe-link-per-recipient')
    DATA.mkdir(exist_ok=True)
    (DATA / 'digest_preview.html').write_text(html, encoding='utf-8')
    print(f'preview: data/digest_preview.html | {total} weekend events, {len(items)} picks | {len(active)} active subscribers')
    if not items:
        print('nothing to send (no weekend events)')
        return
    if not a.send:
        print('dry run: pass --send (optionally --to you@example.com) to send')
        return

    sender = os.environ.get('KE_MAIL_FROM', formataddr(('Toronto Kids Events', 'kidsevents@nowservingto.com')))
    host, port = os.environ.get('KE_SMTP_HOST', 'localhost'), int(os.environ.get('KE_SMTP_PORT', '25'))
    smtp = smtplib.SMTP(host, port, timeout=30)
    if os.environ.get('KE_SMTP_USER'):
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(os.environ['KE_SMTP_USER'], os.environ['KE_SMTP_PASS'])
    targets = {a.to: {'age': ''}} if a.to else active
    sent = failed = 0
    for email, s in targets.items():
        age = s.get('age') or None
        if age not in (None, 'babies', 'toddlers', 'kids'):
            age = None
        its, tot, dys = picks_for(events, age)
        if not its:
            continue
        unsub = unsub_url(email)
        subj, txt, htm = render(its, tot, dys, age, unsub)
        try:
            send(smtp, sender, email, subj, txt, htm, unsub)
            sent += 1
        except Exception as ex:  # keep going; one bad address shouldn't stop the batch
            failed += 1
            print(f'failed {email}: {ex}', file=sys.stderr)
    smtp.quit()
    print(f'sent {sent}, failed {failed}')


if __name__ == '__main__':
    main()
