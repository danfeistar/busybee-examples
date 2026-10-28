# BusyBee examples

Runnable Python examples for the **BusyBee social data API** — public data from TikTok, Instagram, YouTube, X, Douyin and Xiaohongshu through one HTTP interface.

No SDK to install, no dependencies: the client is a single file (`busybee.py`, standard library only, Python 3.8+).

```python
import os
from busybee import BusyBee

bb = BusyBee(os.environ["BUSYBEE_API_KEY"])
page = bb.get_comments("tiktok", "7650540499975081248", limit=50)
print(page["count"], page["cost_usd"], page["balance_usd"])
```

Get a key (free trial credit on sign-up): <https://lucydomi.com/guides/start>

---

## Quick start

```bash
git clone https://github.com/danfeistar/busybee-examples.git
cd busybee-examples
export BUSYBEE_API_KEY=sk-...        # Windows: set BUSYBEE_API_KEY=sk-...

python examples/01_comments_to_csv.py tiktok 7650540499975081248 comments.csv
```

## What is in here

| File | What it does |
|---|---|
| `busybee.py` | Minimal client: `call()` plus one method per endpoint, retries on 429/5xx, raises `BusyBeeError` with the API's own `hint` |
| `examples/01_comments_to_csv.py` | Export comments of one post to CSV (UTF-8 BOM, opens cleanly in Excel) |
| `examples/02_keyword_across_platforms.py` | Same keyword across several platforms, ranked by likes |
| `examples/03_comment_insights.py` | Comment insights: sentiment, question ratio, top phrases, most-liked comments |
| `examples/04_trending_digest.py` | Douyin trending list |

Real output (`python examples/03_comment_insights.py tiktok 7650540499975081248`):

```
样本 40 条（总评论 40）
情绪：正面 8 / 负面 0 / 中性 32
提问：11 条，占 27.5%，说明购买意图
单条最高点赞：12007，平均 576.5
高频词：coffee 12 / butter 12 / canadian 7 / glass 7 / salty 5
花费 $0.003，剩余 $2.8785
```

## Endpoints

All endpoints are `POST https://lucydomi.com/mcp/v1/<tool>`, JSON in, JSON out, `Authorization: Bearer sk-...`.

| Tool | Purpose | Platforms |
|---|---|---|
| `list_platforms` | What is available, per platform (free) | — |
| `search_posts` | Search content by keyword | tiktok, instagram, youtube, twitter, douyin, xiaohongshu |
| `get_post` | One post's detail | same |
| `get_comments` | Comments of one post | same |
| `search_creators` | Find accounts by keyword | tiktok, instagram, youtube, douyin, xiaohongshu |
| `get_creator` | One account's profile | same |
| `list_creator_posts` | Recent posts of one account | same |
| `get_trending` | Trending list | douyin |
| `get_comment_insights` | Aggregated comment analytics | tiktok, douyin, xiaohongshu, … |
| `check_balance` | Balance and current group (free) | — |

## Billing, plainly

- Pay per call. Every billed response returns `cost_usd` (this call) and `balance_usd` (remaining), so a script can stop before it runs dry.
- Failed calls (upstream error, timeout) are **not** charged.
- Overseas platforms work on the free trial credit from sign-up.
- Mainland platforms (Douyin, Xiaohongshu) include **5 free trial calls** on a new account; after that they unlock with a cumulative top-up of $30.

## Error handling

```python
from busybee import BusyBee, BusyBeeError

try:
    bb.search_posts("douyin", "咖啡", limit=20)
except BusyBeeError as e:
    print(e.code, e)        # e.g. forbidden 国内平台试用次数已用完 [forbidden]
    print(e.hint)           # the API's own suggestion, if any
```

`BusyBeeError` carries `code`, `hint`, `status` and the raw `payload`, so you can branch on `e.code` (`unauthorized`, `forbidden`, `rate_limited`, `upstream_error`).

## Known limits (honest list)

- Douyin `search_posts` often returns `stats.comments/shares/views = 0`; use `get_post` for the accurate counters.
- `created_at` can be `null` on Xiaohongshu notes; a few notes come back as `normalize_failed`.
- Douyin trending rank 1 sometimes reports `hot_value = 0` — sort by `rank`, not by `hot_value`.
- Reply threads (楼中楼) are counted (`replies`) but not expanded.
- Rate limits apply per key; the client retries 429 with backoff.

## MCP server

If you would rather use this from an AI client (Claude Desktop, Cursor, Cline, n8n…) instead of HTTP, use the MCP server: <https://github.com/danfeistar/busybee-mcp>

## 中文说明

同一份代码的中文用法：

- 只依赖 Python 标准库，`busybee.py` 一个文件就是客户端；
- `examples/` 下四个脚本可直接跑：评论导 CSV、多平台关键词对比、评论洞察、抖音热榜；
- 每次调用返回里都有 `cost_usd`（本次花费）和 `balance_usd`（剩余余额），失败调用不扣费；
- 海外平台（TikTok / Instagram / YouTube / X）注册赠体验金即可调用；国内平台（抖音 / 小红书）新账户有 5 次免费试用，用完需累计充值满 $30 解锁；
- 密钥入口：<https://lucydomi.com/guides/start>

## License

MIT
