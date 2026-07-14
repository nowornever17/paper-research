"""工具模块 — 日志 + 辅助函数"""
import logging
import sys

# ── 日志 ──
def get_logger(name: str = "paper_research") -> logging.Logger:
    """获取统一格式的 logger"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "[%(levelname)s] %(asctime)s %(message)s",
            datefmt="%H:%M:%S"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


log = get_logger()
