"""
城市设计案例研究助手 — 配置文件
=================================
支持两种配置方式：

① .env 文件（推荐）: cp .env.example .env → 填入 Key
② 直接编辑本文件 : 填入下方对应变量

.env 优先级更高——如果 .env 存在，本文件中的值会被覆盖。
"""

import os

# ── 尝试从 .env 加载（可选依赖）──
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 未安装，使用本文件中的值

# ── 多选一：填入对应密钥，其余留空 ──

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ZHIPU_API_KEY     = os.getenv("ZHIPU_API_KEY", "")
QWEN_API_KEY      = os.getenv("QWEN_API_KEY", "")
MOONSHOT_API_KEY  = os.getenv("MOONSHOT_API_KEY", "")
ERNIE_API_KEY     = os.getenv("ERNIE_API_KEY", "")

ACTIVE_API = os.getenv("ACTIVE_API", "deepseek")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./research_output")

# ── 接口参数（通常不需要修改）──

API_REGISTRY = {
    "deepseek": {
        "key":      DEEPSEEK_API_KEY,
        "base_url": "https://api.deepseek.com",
        "model":    "deepseek-chat",
        "label":    "DeepSeek V3",
    },
    "zhipu": {
        "key":      ZHIPU_API_KEY,
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model":    "glm-4-flash",
        "label":    "智谱 GLM-4-Flash【免费】",
    },
    "qwen": {
        "key":      QWEN_API_KEY,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model":    "qwen-turbo",
        "label":    "通义千问 Turbo",
    },
    "moonshot": {
        "key":      MOONSHOT_API_KEY,
        "base_url": "https://api.moonshot.cn/v1",
        "model":    "moonshot-v1-8k",
        "label":    "Moonshot (Kimi)",
    },
    "ernie": {
        "key":      ERNIE_API_KEY,
        "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
        "model":    "ernie-speed-128k",
        "label":    "百度文心 ERNIE",
    },
}
