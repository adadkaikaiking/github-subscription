"""推送模块 - 支持 Server酱 和 WxPusher 两种渠道。"""

import logging

import httpx

logger = logging.getLogger(__name__)

SERVERCHAN_URL = "https://sct.ftqq.com/{key}.send"
WXPUSHER_URL = "https://wxpusher.zjiecode.com/api/send/message"


def push(title: str, body: str, push_type: str, push_token: str) -> bool:
    """推送消息到微信。

    Args:
        title: 消息标题。
        body: 消息正文（Markdown）。
        push_type: "serverchan" 或 "wxpusher"。
        push_token: Server酱 SendKey 或 WxPusher appToken。

    Returns:
        推送成功返回 True，否则 False。
    """
    if not push_token:
        logger.warning("PUSH_TOKEN 未设置，跳过推送")
        _dry_run_print(title, body)
        return False

    if push_type == "wxpusher":
        return _push_wxpusher(title, body, push_token)
    return _push_serverchan(title, body, push_token)


def _push_serverchan(title: str, body: str, key: str) -> bool:
    """通过 Server酱 推送。"""
    url = SERVERCHAN_URL.format(key=key)
    try:
        resp = httpx.post(url, data={"title": title, "desp": body}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            logger.info("Server酱 推送成功")
            return True
        logger.warning("Server酱 推送返回异常: %s", data)
        return False
    except Exception as exc:
        logger.error("Server酱 推送失败: %s", exc)
        return False


def _push_wxpusher(title: str, body: str, app_token: str) -> bool:
    """通过 WxPusher 推送。

    注意：需要先在 WxPusher 创建应用并获取 appToken，用户需扫码关注。
    """
    payload = {
        "appToken": app_token,
        "content": f"# {title}\n\n{body}",
        "contentType": 2,  # Markdown
        "summary": title,
    }
    try:
        resp = httpx.post(WXPUSHER_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 1000:
            logger.info("WxPusher 推送成功")
            return True
        logger.warning("WxPusher 推送返回异常: %s", data)
        return False
    except Exception as exc:
        logger.error("WxPusher 推送失败: %s", exc)
        return False


def _dry_run_print(title: str, body: str) -> None:
    """无 token 时在控制台打印消息内容。"""
    sep = "=" * 48
    print(f"\n{sep}")
    print(f"  {title}")
    print(sep)
    print(body)
    print(f"{sep}\n")