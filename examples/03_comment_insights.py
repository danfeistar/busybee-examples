#!/usr/bin/env python3
"""一条内容的评论洞察：情绪分布、提问占比、高频词、最高赞评论。

用法：
    export BUSYBEE_API_KEY=sk-...
    python examples/03_comment_insights.py tiktok 7650540499975081248
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from busybee import BusyBee

platform = sys.argv[1] if len(sys.argv) > 1 else "tiktok"
post_id = sys.argv[2] if len(sys.argv) > 2 else "7650540499975081248"

bb = BusyBee()
d = bb.get_comment_insights(platform, post_id, sample=40)

sen = d.get("sentiment") or {}
q = d.get("questions") or {}
eng = d.get("engagement") or {}

print("样本 %s 条（总评论 %s）" % (d.get("sampled"), d.get("total")))
print("情绪：正面 %s / 负面 %s / 中性 %s" % (sen.get("positive"), sen.get("negative"), sen.get("neutral")))
print("提问：%s 条，占 %.1f%%，说明购买意图" % (q.get("count"), (q.get("ratio") or 0) * 100))
print("单条最高点赞：%s，平均 %s" % (eng.get("max_likes"), eng.get("avg_likes")))
print("\n高频词：")
for p in (d.get("top_phrases") or [])[:8]:
    print("  %-14s %s 次" % (p.get("phrase"), p.get("count")))
print("\n最高赞评论：")
for c in (d.get("top_liked") or [])[:3]:
    print("  [%s赞] %s" % (c.get("likes"), (c.get("text") or "")[:60]))
print("\n一句话总结：%s" % d.get("summary", ""))
print("花费 $%s，剩余 $%s" % (d.get("cost_usd"), d.get("balance_usd")))
