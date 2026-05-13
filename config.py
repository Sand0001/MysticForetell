import os

# ===================== 1. 大模型 (LLM) 相关配置 =====================
# 这里复用了用户之前的 SiliconFlow 配置
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "sk-gbvhusgowwvupxznwmsrolmwlqnvcldnhfakuvkonqftxtxv")
LLM_BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"
# LLM_MODEL = "THUDM/GLM-Z1-9B-0414"
LLM_MODEL ="THUDM/GLM-4-9B-0414"
LLM_TEMPERATURE = 0.8
LLM_TIMEOUT = 60.0

# ===================== 2. 服务端配置 =====================
SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.getenv("PORT", 80))

# ===================== 3. 占卜系统配置 =====================
# 可以在这里定义一些通用的占卜参数
DEFAULT_SYSTEM_PROMPT = "你是一位精通东西方神秘学的占卜大师，语气庄重且充满智慧。"
