# Telegram 公告機器人 📢

這是一個用於管理和發送 Telegram 群組/頻道公告的機器人。

## 主要功能

🔑 **權限管理**
- 支持超級管理員和普通管理員角色
- 通過 .env 配置文件靈活設置管理員權限

📝 **公告發送**
- 支持向多個群組/頻道同時發送公告
- 支持文字格式化（粗體、斜體、連結等）
- 提供公告預覽功能

🏠 **群組/頻道管理**
- 支持多群組和頻道配置 
- 可在 .env 中輕鬆添加/移除群組和頻道

⚙️ **配置簡單**
- 使用 .env 文件進行配置
- 提供 .env.example 作為配置範例
- 支持熱重載配置

## 環境要求
- Python 3.8+
- Docker (可選)
- python-telegram-bot
- python-dotenv

## 快速開始

### 本地運行
1. 複製 `.env.example` 為 `.env`
2. 在 `.env` 中填入以下配置:
   - `BOT_TOKEN`: Telegram Bot Token
   - `SUPER_ADMIN_ID`: 超級管理員的 Telegram ID
   - `ADMIN_IDS`: 普通管理員的 Telegram ID (多個ID用逗號分隔)
   - `TARGET_GROUPS`: 目標群組/頻道的 ID (多個ID用逗號分隔)
3. 安裝依賴套件:
   ```bash
   pip install -r requirements.txt
   ```
4. 運行機器人:
   ```bash
   python src/bot/announcement_bot.py
   ```

### Docker 運行
1. 複製 `.env.example` 為 `.env` 並填入相關配置
2. 使用 docker-compose 啟動:
   ```bash
   docker-compose up -d
   ```
3. 查看日誌:
   ```bash
   docker-compose logs -f
   ```

## 在 Telegram 中使用 BotFather 設置以下命令：

- `/start` - 顯示歡迎信息和機器人狀態
- `/announce` - 開始發送公告流程
- `/cancel` - 取消當前操作
