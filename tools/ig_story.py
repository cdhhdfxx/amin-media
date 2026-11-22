#!/usr/bin/env python3
"""Publish pre-hosted story images: ig_story.py stories/<folder>  (each NN.jpg becomes one story, in order)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_publish import call, wait_ready, IG_USER, REPO
REPO_DIR = os.environ.get("AMIN_MEDIA_DIR", "/home/user/amin-media")
rel = sys.argv[1].strip("/")
for p in sorted(glob.glob(os.path.join(REPO_DIR, rel, "*.jpg"))):
    url = f"https://raw.githubusercontent.com/{REPO}/main/{rel}/{os.path.basename(p)}"
    cid = call(f"{IG_USER}/media", {"image_url": url, "media_type": "STORIES"}, "POST")["id"]
    wait_ready(cid)
    mid = call(f"{IG_USER}/media_publish", {"creation_id": cid}, "POST")["id"]
    print("STORY PUBLISHED:", os.path.basename(p), mid)
