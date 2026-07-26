"""格式化模块 - 将项目列表格式化为适合微信推送的消息。"""

import datetime
from typing import Any

MAX_DESC_LENGTH = 80


def format_message(projects: list[dict[str, Any]]) -> tuple[str, str]:
    """格式化项目列表，返回 (title, body) 用于推送。

    Args:
        projects: fetcher.fetch() 返回的项目列表。

    Returns:
        (title, body) 标题与正文，正文为 Markdown 格式。
    """
    today = datetime.date.today().isoformat()
    title = f"📌 GitHub 热门项目日报 {today}"

    if not projects:
        body = "今日暂无数据。"
        return title, body

    lines = [f"# GitHub 趋势榜 {today}\n"]
    for i, proj in enumerate(projects, 1):
        name = proj.get("name", "unknown")
        url = proj.get("url", "")
        desc = proj.get("description", "")
        stars = proj.get("stars", 0)
        lang = proj.get("language", "")
        stars_today = proj.get("stars_today", 0)

        if desc and len(desc) > MAX_DESC_LENGTH:
            desc = desc[: MAX_DESC_LENGTH - 1] + "…"

        line = f"### {i}. [{name}]({url})\n"
        if desc:
            line += f"> {desc}\n"
        parts = []
        if lang:
            parts.append(f"🛠 {lang}")
        parts.append(f"⭐ {stars}")
        if stars_today:
            parts.append(f"📈 +{stars_today} today")
        line += " | ".join(parts)
        lines.append(line)

    lines.append(f"\n---\n🔄 数据来源: GitHub Search API / Trending")
    body = "\n\n".join(lines)
    return title, body