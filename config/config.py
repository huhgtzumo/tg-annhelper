import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

def safe_int_convert(value, default=None):
    """安全地轉換字符串到整數"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN 未設置")

# 群組配置
GROUPS = {}
if os.getenv('GROUP1_ID'):
    GROUPS["group1"] = {
        "id": safe_int_convert(os.getenv('GROUP1_ID')),
        "name": os.getenv('GROUP1_NAME', 'Group 1')
    }
if os.getenv('GROUP2_ID'):
    GROUPS["group2"] = {
        "id": safe_int_convert(os.getenv('GROUP2_ID')),
        "name": os.getenv('GROUP2_NAME', 'Group 2')
    }

# 頻道配置
CHANNELS = {}
if os.getenv('CHANNEL1_ID'):
    CHANNELS["channel1"] = {
        "id": safe_int_convert(os.getenv('CHANNEL1_ID')),
        "name": os.getenv('CHANNEL1_NAME', 'Channel 1')
    }
if os.getenv('CHANNEL2_ID'):
    CHANNELS["channel2"] = {
        "id": safe_int_convert(os.getenv('CHANNEL2_ID')),
        "name": os.getenv('CHANNEL2_NAME', 'Channel 2')
    }

# 超級管理員 ID 列表
SUPER_ADMIN_ID = safe_int_convert(os.getenv('SUPER_ADMIN_ID'))
if not SUPER_ADMIN_ID:
    raise ValueError("SUPER_ADMIN_ID 未設置")
SUPER_ADMIN_IDS = [SUPER_ADMIN_ID]

# 普通管理員 ID 列表
ADMIN_IDS = os.getenv('ADMIN_USER_IDS', '').split(',')
ADMIN_USER_IDS = [safe_int_convert(id_str) for id_str in ADMIN_IDS if id_str.strip()]