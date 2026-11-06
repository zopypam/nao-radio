#!/usr/bin/env python3
"""Fill missing link.image in episode JSONs from each item's OWN source page.

For every news item whose link has no image, fetch the item's url (or link.url),
read og:image / twitter:image from the page head, and store the absolute URL.
YouTube items use their own video thumbnail (deterministic from the video id).
Items whose page has no usable image are left untouched (the player's chart /
relation-diagram layer covers them). Never substitutes stock or generated images.

usage: python3 tools-local/fetch_images.py [episodes/XXXX-ja.json ...]
"""
import json, re, sys, urllib.request, urllib.parse, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}

def og_image(url):
    if "youtube.com/watch" in url or "youtu.be/" in url:
        m = re.search(r"(?:v=|youtu\.be/)([\w-]{6,})", url)
        if m:
            return f"https://i.ytimg.com/vi/{m.group(1)}/hqdefault.jpg"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=12) as r:
            head = r.read(262144).decode("utf-8", "ignore")
            final = r.geturl()
    except Exception as e:
        print(f"  fetch failed: {url} ({e})")
        return None
    for pat in (r'property=["\']og:image(?::secure_url)?["\']\s+content=["\']([^"\']+)',
                r'content=["\']([^"\']+)["\']\s+property=["\']og:image',
                r'name=["\']twitter:image["\']\s+content=["\']([^"\']+)',
                r'content=["\']([^"\']+)["\']\s+name=["\']twitter:image'):
        m = re.search(pat, head)
        if m:
            return urllib.parse.urljoin(final, m.group(1).replace("&amp;", "&"))
    return None

def main(paths):
    total_filled = total_missing = 0
    for p in paths:
        ep = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        changed = False
        for n in ep.get("news", []):
            link = n.get("link") or {}
            if link.get("image"):
                continue
            url = link.get("url") or n.get("url")
            if not url:
                total_missing += 1
                print(f"  no url: {n.get('label')}")
                continue
            img = og_image(url)
            if img:
                if not n.get("link"):
                    n["link"] = {"url": url, "title": n.get("label", ""), "site": urllib.parse.urlparse(url).hostname, "description": "", "icon": None}
                n["link"]["image"] = img
                changed = True
                total_filled += 1
                print(f"  filled: {n.get('label')} -> {img[:90]}")
            else:
                total_missing += 1
                print(f"  no image at source: {n.get('label')}")
        if changed:
            pathlib.Path(p).write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"updated {p}")
    print(f"filled={total_filled} still_missing={total_missing}")

if __name__ == "__main__":
    args = sys.argv[1:] or [str(p) for p in sorted((ROOT / "episodes").glob("*.json"))]
    main(args)
