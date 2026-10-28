#!/usr/bin/env python3
"""同一个关键词，一次跑多个平台，输出互动量排行。

用法：
    export BUSYBEE_API_KEY=sk-...
    python examples/02_keyword_across_platforms.py coffee tiktok youtube
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from busybee import BusyBee, BusyBeeError

keyword = sys.argv[1] if len(sys.argv) > 1 else "coffee"
platforms = sys.argv[2:] or ["tiktok", "youtube", "instagram"]

bb = BusyBee()
collected = []

for p in platforms:
    try:
        page = bb.search_posts(p, keyword, limit=10)
    except BusyBeeError as e:
        print("跳过 %-12s %s" % (p, e))
        continue
    for item in page.get("items", []):
        stats = item.get("stats") or {}
        collected.append({
            "platform": p,
            "author": (item.get("author") or {}).get("handle") or "",
            "likes": stats.get("likes") or 0,
            "views": stats.get("views") or 0,
            "text": (item.get("text") or "")[:40],
        })

collected.sort(key=lambda x: (x["likes"], x["views"]), reverse=True)
print("%-10s %-22s %10s %12s  %s" % ("平台", "作者", "点赞", "播放", "文案"))
for c in collected[:15]:
    print("%-10s %-22s %10d %12d  %s" % (c["platform"], c["author"][:22], c["likes"], c["views"], c["text"]))

print("\n共 %d 条，花费 $%.4f" % (len(collected), bb.spent_usd))
