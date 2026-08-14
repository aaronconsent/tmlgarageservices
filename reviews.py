#!/usr/bin/env python3
"""Pull TML's real Google reviews via DataForSEO Business Data API.

Place ID comes from the site's own (quota-broken) Elfsight widget config.
Caches to data-reviews/reviews.json; pass --fresh to re-pull (billed ~$0.05).
Credentials via env DATAFORSEO_LOGIN/DATAFORSEO_PASSWORD (or DFS_*).
"""
import base64
import json
import os
import sys
import time
import urllib.request

PLACE_ID = "ChIJGcCLGTc7R4YR9gwp3xFvXps"
DATA = os.path.join(os.path.dirname(__file__), "data-reviews")
os.makedirs(DATA, exist_ok=True)
CACHE = os.path.join(DATA, "reviews.json")

if os.path.exists(CACHE) and "--fresh" not in sys.argv:
    print("cached reviews.json exists (use --fresh to re-pull)")
    sys.exit(0)

LOGIN = os.environ.get("DFS_LOGIN") or os.environ.get("DATAFORSEO_LOGIN")
PASSWORD = os.environ.get("DFS_PASSWORD") or os.environ.get("DATAFORSEO_PASSWORD")
if not LOGIN or not PASSWORD:
    sys.exit("Set DATAFORSEO_LOGIN/DATAFORSEO_PASSWORD env vars first.")
AUTH = base64.b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()

def call(path, payload=None, method="POST"):
    req = urllib.request.Request(
        "https://api.dataforseo.com/v3" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Basic " + AUTH, "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

post = call("/business_data/google/reviews/task_post",
            [{"place_id": PLACE_ID, "language_code": "en", "location_code": 2840, "depth": 30}])
task = post["tasks"][0]
if task["status_code"] not in (20000, 20100):
    sys.exit(f"task_post failed: {task['status_message']}")
tid = task["id"]
print(f"task {tid} posted (cost ${post.get('cost', 0):.4f}); polling...")

for attempt in range(30):
    time.sleep(10)
    got = call(f"/business_data/google/reviews/task_get/{tid}", method="GET")
    t = got["tasks"][0]
    if t["status_code"] == 20000 and t.get("result"):
        with open(CACHE, "w") as f:
            json.dump(got, f, indent=1)
        res = t["result"][0]
        print(f"rating {res.get('rating', {}).get('value')} from "
              f"{res.get('reviews_count')} reviews; pulled {len(res.get('items') or [])} items")
        sys.exit(0)
    print(f"  attempt {attempt + 1}: {t['status_message']}")
sys.exit("task did not complete in time")
