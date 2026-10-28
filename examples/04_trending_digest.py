#!/usr/bin/env python3
"""抖音热榜速览（只支持抖音）。

用法：
    export BUSYBEE_API_KEY=sk-...
    python examples/04_trending_digest.py [limit]
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from busybee import BusyBee, BusyBeeError

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20

bb = BusyBee()
try:
    data = bb.get_trending("douyin", limit=limit)
except BusyBeeError as e:
    # 热榜目前只有抖音，属于国内分组：新账户有 5 次免费试用，
    # 用完后需累计充值满 $30 解锁国内平台。
    raise SystemExit("热榜调用失败：%s" % e)

# 注意：热榜首位偶尔 hot_value=0，排序请以 rank 为准，不要按 hot_value 重排。
items = sorted(data.get("items", []), key=lambda x: x.get("rank") or 0)
for t in items:
    print("%2s. %s（热度 %s）" % (t.get("rank"), t.get("title"), t.get("hot_value")))

print("\n共 %s 条，花费 $%s" % (data.get("count"), data.get("cost_usd")))
