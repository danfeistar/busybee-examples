"""Minimal BusyBee API client (standard library only, no dependencies).

BusyBee exposes social-media public data for TikTok, Instagram, YouTube, X,
Douyin and Xiaohongshu through plain HTTP endpoints.

    from busybee import BusyBee
    bb = BusyBee(os.environ["BUSYBEE_API_KEY"])
    page = bb.search_posts("tiktok", "coffee", limit=10)
    for item in page["items"]:
        print(item["author"]["handle"], item["stats"]["likes"])

Every billed response carries `cost_usd` (this call) and `balance_usd`
(remaining), so you can stop before running out.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("BUSYBEE_BASE_URL", "https://lucydomi.com/mcp/v1")


class BusyBeeError(RuntimeError):
    """Raised when the API returns ok=false or an HTTP error."""

    def __init__(self, message, *, code=None, hint=None, status=None, payload=None):
        super().__init__(message)
        self.code = code
        self.hint = hint
        self.status = status
        self.payload = payload or {}

    def __str__(self):
        bits = [super().__str__()]
        if self.code:
            bits.append("[%s]" % self.code)
        if self.hint:
            bits.append("hint: %s" % self.hint)
        return " ".join(bits)


class BusyBee:
    def __init__(self, api_key=None, base_url=BASE_URL, timeout=120, retries=2):
        self.api_key = api_key or os.environ.get("BUSYBEE_API_KEY", "")
        if not self.api_key:
            raise SystemExit("缺少密钥：设置环境变量 BUSYBEE_API_KEY=sk-...")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.spent_usd = 0.0
        self.balance_usd = None

    # ── transport ────────────────────────────────────────────────────────
    def call(self, tool, **params):
        """Call one endpoint and return the decoded JSON payload."""
        url = "%s/%s" % (self.base_url, tool)
        body = json.dumps(params, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": "Bearer %s" % self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "busybee-examples/1.0 (+https://lucydomi.com)",
        }
        last = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    data = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", "ignore")
                try:
                    data = json.loads(raw)
                except Exception:
                    data = {"ok": False, "error": "http_%d" % e.code, "message": raw[:200]}
                # 429 / 5xx 重试，其余直接抛
                if e.code in (429, 500, 502, 503, 504) and attempt < self.retries:
                    last = data
                    time.sleep(2 * (attempt + 1))
                    continue
                raise BusyBeeError(
                    data.get("message") or data.get("error") or "HTTP %d" % e.code,
                    code=data.get("error"), hint=data.get("hint"), status=e.code, payload=data,
                ) from None
            except urllib.error.URLError as e:
                if attempt < self.retries:
                    last = {"ok": False, "error": "network", "message": str(e.reason)}
                    time.sleep(2 * (attempt + 1))
                    continue
                raise BusyBeeError("网络错误：%s" % e.reason, code="network") from None
        else:  # pragma: no cover - 只在全部重试失败时走到
            raise BusyBeeError(
                (last or {}).get("message", "请求失败"),
                code=(last or {}).get("error"),
            )

        if not data.get("ok", True):
            raise BusyBeeError(
                data.get("message") or data.get("error") or "调用失败",
                code=data.get("error"), hint=data.get("hint"), payload=data,
            )

        if "cost_usd" in data:
            self.spent_usd += float(data.get("cost_usd") or 0)
        if "balance_usd" in data:
            self.balance_usd = data.get("balance_usd")
        return data

    # ── endpoints ────────────────────────────────────────────────────────
    def list_platforms(self):
        return self.call("list_platforms")

    def search_posts(self, platform, keyword, limit=20):
        return self.call("search_posts", platform=platform, keyword=keyword, limit=limit)

    def get_post(self, platform, post_id):
        return self.call("get_post", platform=platform, post_id=post_id)

    def get_comments(self, platform, post_id, limit=20):
        return self.call("get_comments", platform=platform, post_id=post_id, limit=limit)

    def get_trending(self, platform="douyin", limit=20):
        return self.call("get_trending", platform=platform, limit=limit)

    def search_creators(self, platform, keyword, limit=10):
        return self.call("search_creators", platform=platform, keyword=keyword, limit=limit)

    def get_creator(self, platform, creator):
        return self.call("get_creator", platform=platform, creator=creator)

    def list_creator_posts(self, platform, creator, limit=10):
        return self.call("list_creator_posts", platform=platform, creator=creator, limit=limit)

    def get_comment_insights(self, platform, post_id, sample=40):
        return self.call("get_comment_insights", platform=platform, post_id=post_id, sample=sample)

    def check_balance(self):
        data = self.call("check_balance")
        self.balance_usd = data.get("quota_usd", self.balance_usd)
        return data
