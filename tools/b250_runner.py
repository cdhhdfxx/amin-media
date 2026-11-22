#!/usr/bin/env python3
"""Publish b250/NNN carousels on schedule: post n is due at START + (n-1)*15min (Baghdad).
At most one post per cycle, never two within 5 minutes; marks b250/NNN/PUBLISHED.txt and pushes."""
import os, sys, time, glob, datetime, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_publish import call, wait_ready, IG_USER, REPO
R = "/home/user/amin-media"
TZ = datetime.timezone(datetime.timedelta(hours=3))
START = datetime.datetime(2026, 11, 23, 1, 0, tzinfo=TZ)
STEP = datetime.timedelta(minutes=15)
LOG = os.path.join(R, "b250", "runner.log")
def log(m):
    line = f"[{datetime.datetime.now(TZ):%m-%d %H:%M:%S}] {m}"; print(line, flush=True)
    open(LOG, "a").write(line + "\n")
def git(*a): return subprocess.run(["git", "-C", R, *a], capture_output=True, text=True)
def publish(n):
    d = f"b250/{n:03d}"; imgs = sorted(os.path.basename(p) for p in glob.glob(f"{R}/{d}/0*.jpg"))
    cap = open(f"{R}/{d}/caption.txt", encoding="utf-8").read().strip()
    kids = [call(f"{IG_USER}/media", {"image_url": f"https://raw.githubusercontent.com/{REPO}/main/{d}/{i}", "is_carousel_item": "true"}, "POST")["id"] for i in imgs]
    for k in kids: wait_ready(k)
    cid = call(f"{IG_USER}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": cap}, "POST")["id"]
    wait_ready(cid)
    mid = call(f"{IG_USER}/media_publish", {"creation_id": cid}, "POST")["id"]
    return call(mid, {"fields": "permalink"}).get("permalink", mid)
def public(n, f):
    try: urllib.request.urlopen(urllib.request.Request(f"https://raw.githubusercontent.com/{REPO}/main/b250/{n:03d}/{f}", method="HEAD"), timeout=20); return True
    except Exception: return False
last = 0
while True:
    git("pull", "-q", "--rebase", "origin", "main")
    now = datetime.datetime.now(TZ)
    todo = [n for n in range(1, 251) if not os.path.exists(f"{R}/b250/{n:03d}/PUBLISHED.txt")]
    if not todo: log("ALL DONE"); break
    n = todo[0]; due = START + (n - 1) * STEP
    if now >= due and time.time() - last > 300:
        if not os.path.exists(f"{R}/b250/{n:03d}/caption.txt"): log(f"post {n} due but not designed yet")
        elif not (public(n, "03.jpg") and public(n, "caption.txt")): log(f"post {n} not public yet")
        else:
            try:
                link = publish(n); last = time.time()
                open(f"{R}/b250/{n:03d}/PUBLISHED.txt", "w").write(link + "\n"); log(f"PUBLISHED {n} {link}")
                for _ in range(6):
                    git("add", f"b250/{n:03d}/PUBLISHED.txt", "b250/runner.log")
                    git("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", "commit", "-qm", f"Mark b250 post {n} published\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01XnadP7Md9X1sxfrvtaMyLu")
                    if git("-c", "push.negotiate=true", "push", "-q", "origin", "HEAD:main").returncode == 0: break
                    git("pull", "-q", "--rebase", "origin", "main"); time.sleep(5)
            except BaseException as e:
                if isinstance(e, KeyboardInterrupt): raise
                log(f"ERROR post {n}: {e}"); time.sleep(120)
    time.sleep(20)
