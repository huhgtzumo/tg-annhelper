FROM python:3.9-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程序文件
COPY src/ ./src/
COPY config/ ./config/
COPY .env .

# 設置環境變量
ENV PYTHONPATH=/app

# 運行機器人
CMD ["python", "src/bot/announcement_bot.py"] 