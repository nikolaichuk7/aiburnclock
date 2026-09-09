#!/usr/bin/env python3
"""Send AI Burn Clock press releases through Resend.

Usage:
  python3 send_press.py --list data/press-list.json [--dry-run] [--limit N] [--only national|state|all]

The list is a JSON array of {"outlet","email","beat","state"?,"name"?,"note"?}.
Each recipient gets ONE email: the state release for their state if the outlet is local and that
state has a release today, otherwise the national release. Every send is logged to data/press-log.jsonl
and a recipient is never sent the same release twice.
"""
import argparse, json, os, sys, time, datetime, urllib.request, pathlib, html as H

HERE = pathlib.Path(__file__).parent
SITE = HERE / "site"; DATA = HERE / "data"
LOG = DATA / "press-log.jsonl"
KEY = None
for line in (pathlib.Path.home() / ".aiburnclock" / "env").read_text().splitlines():
    if line.startswith("RESEND_API_KEY="): KEY = line.split("=", 1)[1].strip()
if not KEY: sys.exit("no RESEND_API_KEY in ~/.aiburnclock/env")

def releases():
    idx = json.loads((SITE / "press-index.json").read_text())
    return idx  # [{date, headline, url, image}]

def plain_text(url):
    """Read the plain-text block of a release page from the built site."""
    rel = url.replace("https://aiburnclock.org", "").strip("/")
    p = SITE / rel / "index.html"
    s = p.read_text()
    a = s.index('<pre id="plain">') + len('<pre id="plain">'); b = s.index("</pre>", a)
    return H.unescape(s[a:b]).strip()

def pick(recipient, rels, today):
    st = (recipient.get("state") or "").lower()
    if st:
        for r in rels:
            if r["url"].rstrip("/").endswith(f"/press/{today}-{st}"): return r
    for r in rels:
        if r["url"].rstrip("/").endswith(f"/press/{today}"): return r
    return rels[0]

def already(email, url):
    if not LOG.exists(): return False
    for line in LOG.read_text().splitlines():
        try: e = json.loads(line)
        except Exception: continue
        if e.get("email") == email and e.get("url") == url and e.get("ok"): return True
    return False

def send(to, subject, text, html_body, tags):
    body = json.dumps({"from": "AI Burn Clock <hello@aiburnclock.org>", "to": [to], "reply_to": "hello@aiburnclock.org",
                       "subject": subject, "text": text, "html": html_body, "tags": tags}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=body, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "User-Agent": "aiburnclock-press/1.0 (+https://aiburnclock.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return True, json.load(r)
    except urllib.error.HTTPError as e:
        return False, {"status": e.code, "body": e.read().decode()[:300]}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--list", required=True); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=100); ap.add_argument("--only", default="all"); a = ap.parse_args()
    rels = releases(); today = rels[0]["date"]
    recips = json.loads(pathlib.Path(a.list).read_text())
    sent = 0
    for rc in recips:
        r = pick(rc, rels, today)
        is_state = "-" in r["url"].rstrip("/").split("/")[-1]
        if a.only == "national" and is_state: continue
        if a.only == "state" and not is_state: continue
        if already(rc["email"], r["url"]): print("skip (already sent):", rc["email"], r["url"]); continue
        if sent >= a.limit: print("limit reached"); break
        text = plain_text(r["url"])
        greeting = f"Hello {rc['name'].split()[0]}," if rc.get("name") else f"Hello {rc['outlet']} desk,"
        intro = (f"{greeting}\n\nBelow is today's release from the AI Burn Clock, an independent daily index of what AI agents cost when they read whole files instead of retrieving the passage they need. "
                 f"It is datelined for republication; the plain text, the sources and a 1200x630 image are on the release page: {r['url']}\n"
                 f"Every state has its own release with its own figures; the list is at https://aiburnclock.org/press and the data at https://aiburnclock.org/data.json.\n\n"
                 f"Interviews, data pulls and state or agency memos on request. Reply to this address.\n\n" + "-" * 60 + "\n\n")
        outro = ("\n\n" + "-" * 60 + "\nAI Burn Clock, an independent statistical observatory maintained by the XERJ community. Not affiliated with any government agency. "
                 "Method: https://aiburnclock.org/methodology. If you would rather not receive releases, reply with STOP and we will remove this address.")
        body_text = intro + text + outro
        html_body = ("<div style='font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#1b1b1b;max-width:720px'>"
                     + "<p>" + H.escape(greeting) + "</p>"
                     + "<p>Below is today's release from the <a href='https://aiburnclock.org/'>AI Burn Clock</a>, an independent daily index of what AI agents cost when they read whole files instead of retrieving the passage they need. It is datelined for republication; the plain text, the sources and a 1200×630 image are on the <a href='" + r["url"] + "'>release page</a>. Every state has its own release with its own figures (<a href='https://aiburnclock.org/press'>list</a>, <a href='https://aiburnclock.org/data.json'>data</a>).</p>"
                     + "<p>Interviews, data pulls and state or agency memos on request. Reply to this address.</p><hr>"
                     + "<img src='https://aiburnclock.org/" + r["image"] + "' alt='' width='600' style='max-width:100%;height:auto;border:1px solid #dfe1e2'>"
                     + "<pre style='white-space:pre-wrap;font-family:Georgia,serif;font-size:15px'>" + H.escape(text) + "</pre><hr>"
                     + "<p style='font-size:12.5px;color:#565c65'>AI Burn Clock, an independent statistical observatory maintained by the XERJ community. Not affiliated with any government agency. <a href='https://aiburnclock.org/methodology'>Method</a>. If you would rather not receive releases, reply with STOP and we will remove this address.</p></div>")
        subject = r["headline"]
        if a.dry_run:
            print("DRY:", rc["email"], "<-", r["url"]); sent += 1; continue
        ok, resp = send(rc["email"], subject, body_text, html_body, [{"name": "kind", "value": "press"}, {"name": "release", "value": today}])
        entry = {"ts": datetime.datetime.utcnow().isoformat() + "Z", "email": rc["email"], "outlet": rc["outlet"], "url": r["url"], "ok": ok, "resp": resp}
        with LOG.open("a") as f: f.write(json.dumps(entry) + "\n")
        print("sent" if ok else "FAIL", rc["email"], "<-", r["url"].split("/press/")[-1], resp if not ok else resp.get("id"))
        sent += 1; time.sleep(0.6)  # Resend: 2 requests per second
    print(f"done: {sent} {'planned' if a.dry_run else 'sent'}")

if __name__ == "__main__": main()
