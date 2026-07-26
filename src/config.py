"""配置模块 - 从环境变量读取运行时配置。"""

import os


def load() -> dict:
    """读取并校验环境变量，返回配置字典。"""
    config = {
        "push_token": os.environ.get("PUSH_TOKEN", ""),
        "push_type": os.environ.get("PUSH_TYPE", "pushplus"),
        "github_token": os.environ.get("GITHUB_TOKEN", ""),
    }
    if not config["push_token"]:
        print("[WARNING] PUSH_TOKEN not set, push will be skipped")
    return config