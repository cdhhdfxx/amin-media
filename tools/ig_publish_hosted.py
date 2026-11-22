#!/usr/bin/env python3
"""Publish a pre-hosted post from the amin-media repo: scheduled/<post>/NN.jpg + caption.txt.
Usage: ig_publish_hosted.py post-01 [--dry-run]"""
import sys, os, json, glob, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_publish import call, wait_ready, IG_USER, REPO
REPO_DIR = os.environ.get("AMIN_MEDIA_DIR", "/home/user/amin-media")
post = sys.argv[1]; dry = "--dry-run" in sys.argv
d = os.path.join(REPO_DIR, "scheduled", post)
imgs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*.jpg")))
caption = open(os.path.join(d, "caption.txt"), encoding="utf-8").read().strip()
done = os.path.join(d, "PUBLISHED.txt")
if os.path.exists(done): sys.exit(f"already published: {open(done).read()}")
urls = [f"https://raw.githubusercontent.com/{REPO}/main/scheduled/{post}/{n}" for n in imgs]
if len(urls) == 1:
    cid = call(f"{IG_USER}/media", {"image_url": urls[0], "caption": caption}, "POST")["id"]
else:
    kids = [call(f"{IG_USER}/media", {"image_url": u, "is_carousel_item": "true"}, "POST")["id"] for u in urls]
    for k in kids: wait_ready(k)
    cid = call(f"{IG_USER}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption}, "POST")["id"]
wait_ready(cid)
if dry: print("DRY RUN OK", post, cid); sys.exit()
mid = call(f"{IG_USER}/media_publish", {"creation_id": cid}, "POST")["id"]
link = call(mid, {"fields": "permalink"}).get("permalink")
print("PUBLISHED:", post, link)
