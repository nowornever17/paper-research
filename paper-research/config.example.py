"""
城市设计案例研究助手 — 配置文件
=================================
填写 API 密钥后，与 case_extractor.py 放同一目录即可运行。
三家国内 API 选一家填入，其余留空。
"""

# ──────────────────────────────────────────────────────────────
# 三选一：填入对应密钥，其余留空
# ──────────────────────────────────────────────────────────────

# 【推荐 #1】智谱 GLM-4-Flash —— 完全免费
#   申请：https://open.bigmodel.cn → 注册 → 控制台 → API 密钥 → 新建
#   限额：每天 10 万 tokens，速率 5 次/秒（毕设调研完全够用）
ZHIPU_API_KEY = ""

# 【推荐 #2】DeepSeek —— 几乎免费，100 篇文章约 ¥0.15
#   申请：https://platform.deepseek.com → 注册 → API Keys → 创建密钥
#   价格：deepseek-chat  输入 ¥0.27/M tokens，输出 ¥1.10/M tokens
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"

# 【推荐 #3】通义千问 —— 新用户赠 ¥300 免费额度
#   申请：https://dashscope.aliyuncs.com → 阿里云账号登录 → 开通 → 获取 Key
#   价格：qwen-turbo  输入 ¥0.30/M，输出 ¥0.60/M
QWEN_API_KEY = ""

# ──────────────────────────────────────────────────────────────
# 改这一行来切换供应商：zhipu / deepseek / qwen
# ──────────────────────────────────────────────────────────────
ACTIVE_API = "deepseek"

# ──────────────────────────────────────────────────────────────
# 接口参数（通常不需要修改）
# ──────────────────────────────────────────────────────────────
API_REGISTRY = {
    "zhipu": {
        "key":      ZHIPU_API_KEY,
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model":    "glm-4-flash",
        "label":    "智谱 GLM-4-Flash【完全免费】",
    },
    "deepseek": {
        "key":      DEEPSEEK_API_KEY,
        "base_url": "https://api.deepseek.com",
        "model":    "deepseek-chat",
        "label":    "DeepSeek V3",
    },
    "qwen": {
        "key":      QWEN_API_KEY,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model":    "qwen-turbo",
        "label":    "通义千问 Turbo",
    },
}

# 输出目录（运行时自动创建）
OUTPUT_DIR = "./research_output"
