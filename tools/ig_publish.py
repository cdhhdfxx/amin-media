#!/usr/bin/env python3
"""Publish an image post or carousel to Instagram (@amin_trad_edu) via the Graph API.
Images are pushed to the public GitHub repo (amin-media) so Instagram can fetch them.
Usage: ig_publish.py --caption-file caption.txt img1.png [img2.png ...] [--dry-run]
The Graph API token is injected by the session's network proxy (never stored here)."""
import argparse, json, os, subprocess, sys, time, urllib.parse, urllib.request, shutil, datetime
IG_USER = "17841458087400763"
API = "https://graph.facebook.com/v21.0"
REPO_DIR = os.environ.get("AMIN_MEDIA_DIR", "/home/user/amin-media")
REPO = "cdhhdfxx/amin-media"

def call(path, params=None, method="GET"):
    data = urllib.parse.urlencode(params or {}).encode() if method == "POST" else None
    url = f"{API}/{path}" + ("" if method == "POST" or not params else "?" + urllib.parse.urlencode(params))
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Graph API error {e.code}: {e.read().decode()}")

def to_jpeg(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-q:v", "2", dst], check=True)

def host(images):
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    folder = os.path.join(REPO_DIR, "posts", stamp); os.makedirs(folder, exist_ok=True)
    names = []
    for i, src in enumerate(images, 1):
        name = f"{i:02d}.jpg"; to_jpeg(src, os.path.join(folder, name)); names.append(name)
    subprocess.run(["git", "-C", REPO_DIR, "add", "-A"], check=True)
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-qm", f"post {stamp}"], check=True)
    subprocess.run(["git", "-C", REPO_DIR, "push", "-q", "origin", "HEAD"], check=True)
    urls = [f"https://raw.githubusercontent.com/{REPO}/main/posts/{stamp}/{n}" for n in names]
    for u in urls:  # wait until publicly reachable
        for _ in range(30):
            try:
                urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=15); break
            except Exception: time.sleep(4)
    return urls

def wait_ready(cid):
    for _ in range(40):
        st = call(cid, {"fields": "status_code"}).get("status_code")
        if st == "FINISHED": return
        if st == "ERROR": sys.exit(f"container {cid} failed")
        time.sleep(3)
    sys.exit("timed out waiting for container")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("images", nargs="+"); ap.add_argument("--caption-file", required=True)
    ap.add_argument("--dry-run", action="store_true", help="create containers but do NOT publish")
    a = ap.parse_args(); caption = open(a.caption_file, encoding="utf-8").read().strip()
    urls = host(a.images)
    if len(urls) == 1:
        cid = call(f"{IG_USER}/media", {"image_url": urls[0], "caption": caption}, "POST")["id"]
    else:
        kids = [call(f"{IG_USER}/media", {"image_url": u, "is_carousel_item": "true"}, "POST")["id"] for u in urls]
        for k in kids: wait_ready(k)
        cid = call(f"{IG_USER}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption}, "POST")["id"]
    wait_ready(cid)
    if a.dry_run:
        print("DRY RUN OK - container ready, nothing published:", cid); return
    mid = call(f"{IG_USER}/media_publish", {"creation_id": cid}, "POST")["id"]
    link = call(mid, {"fields": "permalink"}).get("permalink")
    print("PUBLISHED:", link)

if __name__ == "__main__": main()
