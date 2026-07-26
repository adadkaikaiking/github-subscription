"""数据获取模块 - 调用 GitHub Search API 获取近 7 天热门项目。"""

import datetime
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
SEARCH_QUALIFIER = "created:>{}&sort=stars&order=desc"

# Search API 无 token 限频 10次/分钟，有 token 30次/分钟
HEADERS_WITH_TOKEN = {"Accept": "application/vnd.github+json"}
HEADERS_NO_TOKEN = {"Accept": "application/vnd.github+json"}


def fetch(github_token: str = "") -> list[dict[str, Any]]:
    """获取近 7 天 GitHub 星标最多的 10 个项目。

    Args:
        github_token: GitHub Personal Access Token，可选，提高 API 限频。

    Returns:
        项目列表，每项含 name / url / description / stars / language / stars_today。
        异常或空结果时返回 []。
    """
    since = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    query = SEARCH_QUALIFIER.format(since)
    url = f"{GITHUB_API}/search/repositories?q={query}&per_page=10"

    headers = HEADERS_WITH_TOKEN.copy()
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    try:
        resp = httpx.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("GitHub API 请求失败: %s", exc)
        logger.info("降级到爬取 github.com/trending ...")
        return _fetch_trending_fallback()

    items = data.get("items", [])
    if not items:
        logger.info("Search API 返回为空，降级到 trending ...")
        return _fetch_trending_fallback()

    result = []
    for item in items:
        result.append({
            "name": item.get("full_name", ""),
            "url": item.get("html_url", ""),
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language") or "",
            "stars_today": 0,  # Search API 不提供今日增量
        })
    return result


def _fetch_trending_fallback() -> list[dict[str, Any]]:
    """降级方案：爬取 github.com/trending 页面。"""
    url = "https://github.com/trending?since=weekly"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = httpx.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("爬取 trending 也失败了: %s", exc)
        return []

    from html.parser import HTMLParser  # 无额外依赖

    class _Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.projects: list[dict[str, Any]] = []
            self._in_h2 = False
            self._in_desc = False
            self._cur: dict[str, Any] = {}

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag == "h2" and "h3" in attrs_dict.get("class", ""):
                self._in_h2 = True
                self._cur = {"name": "", "url": "", "description": "",
                             "stars": 0, "language": "", "stars_today": 0}
            if tag == "p" and "col-9" in attrs_dict.get("class", ""):
                self._in_desc = True
            if tag == "a" and self._cur and not self._cur["url"]:
                href = attrs_dict.get("href", "")
                if href.startswith("/"):
                    self._cur["url"] = "https://github.com" + href

        def handle_data(self, data):
            if self._in_h2:
                self._cur["name"] = data.strip()
                self._in_h2 = False
            if self._in_desc:
                self._cur["description"] = data.strip()
                self._in_desc = False

        def handle_endtag(self, tag):
            if tag == "article" and self._cur:
                self.projects.append(self._cur)
                self._cur = {}

    parser = _Parser()
    parser.feed(resp.text)
    return parser.projects[:10]