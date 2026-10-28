#!/usr/bin/env python3
"""把一条内容的评论导出成 CSV（Excel 可直接打开）。

用法：
    export BUSYBEE_API_KEY=sk-...
    python examples/01_comments_to_csv.py tiktok 7650540499975081248 out.csv
"""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from busybee import BusyBee

platform = sys.argv[1] if len(sys.argv) > 1 else "tiktok"
post_id = sys.argv[2] if len(sys.argv) > 2 else "7650540499975081248"
out = sys.argv[3] if len(sys.argv) > 3 else "comments.csv"

bb = BusyBee()
page = bb.get_comments(platform, post_id, limit=50)

rows = page.get("items", [])
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["评论人", "评论内容", "点赞", "回复数", "时间", "评论ID"])
    for c in rows:
        author = (c.get("author") or {})
        w.writerow([
            author.get("name") or author.get("handle") or "",
            (c.get("text") or "").replace("\n", " "),
            c.get("likes", 0),
            c.get("replies", 0),
            c.get("created_at") or "",
            c.get("id") or "",
        ])

print("导出 %d 条评论 -> %s" % (len(rows), out))
print("本次花费 $%s，剩余 $%s" % (page.get("cost_usd"), page.get("balance_usd")))
