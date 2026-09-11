#!/usr/bin/env python3
"""Send one-to-one letters through Resend from hello@aiburnclock.org.
Input: JSON list of {to, name, org, subject, body}. Logs to data/letters-log.jsonl; never sends the same (to, subject) twice.
Usage: python3 send_letters.py data/letters-out.json [--dry-run]"""
import json, sys, time, datetime, pathlib, urllib.request, html as H
HERE = pathlib.Path(__file__).parent; LOG = HERE / "data" / "letters-log.jsonl"
KEY = [l.split("=", 1)[1].strip() for l in (pathlib.Path.home() / ".aiburnclock/env").read_text().splitlines() if l.startswith("RESEND_API_KEY=")][0]
def sent_before(to, subject):
    if not LOG.exists(): return False
    for l in LOG.read_text().splitlines():
        if not l.strip(): continue
        e = json.loads(l)
        if e.get("to") == to and e.get("subject") == subject and e.get("ok"): return True
    return False
def send(m):
    text_body = m["body"]; quote = m.get("quote")  # optional: the message we are replying to, appended as a quoted trail
    html_body = "<div style='font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.55;color:#1b1b1b;max-width:680px'>" + "".join(f"<p>{H.escape(p)}</p>" for p in m["body"].split("\n\n"))
    if quote:
        text_body += "\n\n" + "\n".join("> " + l for l in quote.splitlines())
        html_body += "<blockquote style='margin:16px 0 0;padding:0 0 0 12px;border-left:2px solid #c9c9c9;color:#555'>" + "".join(f"<p>{H.escape(p)}</p>" for p in quote.split("\n\n")) + "</blockquote>"
    html_body += "</div>"
    payload = {"from": "Serhii Nikolaichuk, AI Burn Clock <hello@aiburnclock.org>", "to": [m["to"]], "reply_to": "hello@aiburnclock.org", "subject": m["subject"], "text": text_body, "html": html_body, "tags": [{"name": "kind", "value": m.get("kind", "letter")}]}
    if m.get("cc"): payload["cc"] = m["cc"]
    if m.get("headers"): payload["headers"] = m["headers"]  # e.g. In-Reply-To / References so the reply lands in the recipient's thread
    body = json.dumps(payload).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=body, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "User-Agent": "aiburnclock-press/1.0 (+https://aiburnclock.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return True, json.load(r)
    except urllib.error.HTTPError as e: return False, {"status": e.code, "body": e.read().decode()[:300]}
dry = "--dry-run" in sys.argv; letters = json.loads(pathlib.Path(sys.argv[1]).read_text()); n = 0
for m in letters:
    if sent_before(m["to"], m["subject"]): print("skip (sent):", m["to"]); continue
    if dry: print("DRY:", m["to"], "|", m["subject"]); n += 1; continue
    ok, resp = send(m)
    with LOG.open("a") as f: f.write(json.dumps({"ts": datetime.datetime.utcnow().isoformat() + "Z", "to": m["to"], "org": m["org"], "subject": m["subject"], "ok": ok, "resp": resp}) + "\n")
    print("sent" if ok else "FAIL", m["to"], resp.get("id") if ok else resp); n += 1; time.sleep(0.6)
print("done:", n)
