"""GitHub 每日星标趋势推送 - 主入口。"""

import logging

import config
import fetcher
import formatter
import pusher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=== GitHub 每日趋势推送 ===")

    cfg = config.load()

    projects = fetcher.fetch(github_token=cfg["github_token"])
    logger.info("获取到 %d 个项目", len(projects))

    title, body = formatter.format_message(projects)
    logger.info("消息已格式化: %s", title)

    success = pusher.push(
        title=title,
        body=body,
        push_type=cfg["push_type"],
        push_token=cfg["push_token"],
    )

    if success:
        logger.info("推送完成")
    else:
        logger.warning("推送未成功（可能是 token 未配置或推送接口异常）")


if __name__ == "__main__":
    main()