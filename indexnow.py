#!/usr/bin/env python3
"""Submit every URL in site/sitemap.xml to IndexNow (Bing, Yandex, Seznam, Naver) after a deploy."""
import json, re, urllib.request
from pathlib import Path
HERE = Path(__file__).parent
key = (HERE / "data" / "indexnow.key").read_text().strip()
urls = re.findall(r"<loc>(.*?)</loc>", (HERE / "site" / "sitemap.xml").read_text())
body = json.dumps({"host": "aiburnclock.org", "key": key, "keyLocation": f"https://aiburnclock.org/{key}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "aiburnclock/1.0"})
try:
    with urllib.request.urlopen(req, timeout=60) as r: print("IndexNow", r.status, len(urls), "urls")
except urllib.error.HTTPError as e: print("IndexNow HTTP", e.code, e.read()[:200])
