"""
Telegram Announcement Bot
Version: 1.0.1
Author: huhgtzumo
Last updated: 2024-11-07
"""

import os
import sys
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

# 直接讀取配置文件
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'config', 'config.py')

print(f"配置文件路徑: {config_file}")

# 使用 exec 執行配置文件前，創建一個新的命名空間
config_namespace = {}
try:
    with open(config_file, 'r') as f:
        exec(f.read(), config_namespace)
    print("成功導入配置")
    # 從命名空間中獲取所需的變量
    SUPER_ADMIN_IDS = config_namespace['SUPER_ADMIN_IDS']
    ADMIN_USER_IDS = config_namespace['ADMIN_USER_IDS']
    BOT_TOKEN = config_namespace['BOT_TOKEN']
    GROUPS = config_namespace['GROUPS']
    CHANNELS = config_namespace['CHANNELS']
except Exception as e:
    print(f"導入配置時出錯: {e}")
    print(f"配置文件是否存在: {os.path.exists(config_file)}")
    sys.exit(1)

# 定義對話狀態
WAITING_FOR_CONTENT, WAITING_FOR_GROUP = range(2)

# 用於暫存公告內容的字典
announcement_cache = {}

def is_admin(user_id: int) -> bool:
    """檢查用戶是否是管理員"""
    return user_id in SUPER_ADMIN_IDS or user_id in ADMIN_USER_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 命令"""
    # 檢查是否在群組中
    if update.effective_chat.type in ['group', 'supergroup']:
        # 檢查是否是管理員
        if update.effective_user.id not in ADMIN_USER_IDS:
            # 普通用戶在群組中使用命令，直接忽略
            return
    
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title
    
    await update.message.reply_text(
        f'歡迎使用公告機器人！\n'
        f'管理員可以使用 /announce 發送公告。\n\n'
        f'當前聊天 ID：{chat_id}\n'
        f'類型：{chat_type}\n'
        f'名稱：{chat_title if chat_title else "私聊"}'
    )

async def announce_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """開始公告流程"""
    user_id = update.effective_user.id
    print(f"收到 /announce 命令，用戶ID: {user_id}")
    print(f"SUPER_ADMIN_IDS: {SUPER_ADMIN_IDS}")  # 檢查超級管理員列表
    print(f"用戶是否為超級管理員: {user_id in SUPER_ADMIN_IDS}")  # 檢查用戶是否在列表中
    
    # 檢查是否在群組中
    if update.effective_chat.type in ['group', 'supergroup']:
        print(f"在群組中使用命令: {update.effective_chat.title}")
        if user_id not in ADMIN_USER_IDS and user_id not in SUPER_ADMIN_IDS:
            print(f"用戶不是管理員或超級管理員，忽略命令")
            return
    
    # 檢查是否是管理員或超級管理員（私聊時也需要檢查）
    if user_id not in ADMIN_USER_IDS and user_id not in SUPER_ADMIN_IDS:
        print(f"用戶是管理員或超級管理員，拒絕訪問")
        await update.message.reply_text("抱歉，只有管理員可以發送公告。")
        return ConversationHandler.END
    
    usage = """
請按照以下格式發送公告內容：

範例：
這是測試公告 🎉
%%
按鈕1 - https://google.com && 按鈕2 - https://t.me/example

說明：
• 第一行寫公告內容
• 用 %% 分隔內容和按鈕
• 按鈕格式為：按鈕文字 - 網址
• 同一行多個按鈕用 && 分隔
• 不同行的按鈕會顯示在不同行
"""
    
    await update.message.reply_text(usage)
    return WAITING_FOR_CONTENT

def create_group_selection_keyboard():
    """創建群組和頻道選擇鍵盤"""
    keyboard = []
    
    # 添加群組和頻道按鈕，每個一行
    for group_id, group_info in GROUPS.items():
        keyboard.append([InlineKeyboardButton(f"👥 {group_info['name']}", callback_data=f"group_{group_id}")])
    
    for channel_id, channel_info in CHANNELS.items():
        keyboard.append([InlineKeyboardButton(f"📢 {channel_info['name']}", callback_data=f"channel_{channel_id}")])
    
    # 添加取消按鈕
    keyboard.append([InlineKeyboardButton("❌ 取消操作", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

async def process_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理用戶發送的公告內容"""
    try:
        message_text = update.message.text
        print(f"收到公告內容：{message_text}")
        
        # 檢查是否包含 %%
        if '%%' not in message_text:
            await update.message.reply_text("錯誤：消息格式不正確，需要使用 %% 分隔內容和按鈕")
            return WAITING_FOR_CONTENT
            
        # 分割內容和按鈕
        content, buttons_text = message_text.split('%%', 1)
        content = content.strip()
        buttons_text = buttons_text.strip()
        
        if not content or not buttons_text:
            await update.message.reply_text("錯誤：公告內容和按鈕部分都不能為空")
            return WAITING_FOR_CONTENT
        
        # 處理按鈕
        buttons = []
        button_rows = buttons_text.split('\n')
        
        for row in button_rows:
            if not row.strip():
                continue
                
            row_buttons = []
            button_pairs = row.strip().split('&&')
            
            for pair in button_pairs:
                pair = pair.strip()
                if not pair:
                    continue
                    
                if ' - ' not in pair:
                    await update.message.reply_text(f"錯誤：按鈕格式錯誤 '{pair}'\n正確格式應為：按鈕文字 - 網址")
                    return WAITING_FOR_CONTENT
                    
                text, url = pair.split(' - ')
                text = text.strip()
                url = url.strip()
                
                if not text or not url:
                    await update.message.reply_text("錯誤：按鈕文字和網址都不能為空")
                    return WAITING_FOR_CONTENT
                    
                if not (url.startswith('http://') or url.startswith('https://') or url.startswith('t.me/')):
                    await update.message.reply_text(f"錯誤：無效的URL '{url}'\n網址必須以 http://, https:// 或 t.me/ 開頭")
                    return WAITING_FOR_CONTENT
                    
                row_buttons.append(InlineKeyboardButton(text, url=url))
            
            if row_buttons:
                buttons.append(row_buttons)
        
        if not buttons:
            await update.message.reply_text("錯誤：沒有有效的按鈕")
            return WAITING_FOR_CONTENT
            
        # 創建按鈕鍵盤並保存公告內容
        keyboard = InlineKeyboardMarkup(buttons)
        user_id = update.effective_user.id
        announcement_cache[user_id] = {
            'content': content,
            'keyboard': keyboard
        }
        
        # 發送預覽和群組擇按鈕
        await update.message.reply_text(
            f"📢 以下是你的公告預覽：\n\n{content}",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        await update.message.reply_text(
            "請選擇要發送到的群組：",
            reply_markup=create_group_selection_keyboard()
        )
        
        return WAITING_FOR_GROUP
        
    except Exception as e:
        print(f"處理公告時出錯：{str(e)}")
        await update.message.reply_text(f"發生錯誤：{str(e)}\n請重試")
        return WAITING_FOR_CONTENT

async def handle_group_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理群組和頻道選擇"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        
        # 添加對取消操作的處理
        if query.data == "cancel":
            if user_id in announcement_cache:
                del announcement_cache[user_id]
            await query.message.edit_text("❌ 已取消發送公告")
            return ConversationHandler.END
            
        # 處理頻道選擇
        if query.data.startswith("channel_"):
            channel_id = query.data.replace("channel_", "")
            destination_type = "頻道"
            
            if channel_id not in CHANNELS:
                await query.message.edit_text("錯誤：無效的頻道選擇")
                return ConversationHandler.END
            
            destination_id = CHANNELS[channel_id]['id']
            destination_name = CHANNELS[channel_id]['name']
            
        # 處理群組選擇
        elif query.data.startswith("group_"):
            group_id = query.data.replace("group_", "")
            destination_type = "群組"
            
            if group_id not in GROUPS:
                await query.message.edit_text("錯誤：無效的群組選擇")
                return ConversationHandler.END
            
            destination_id = GROUPS[group_id]['id']
            destination_name = GROUPS[group_id]['name']
            
        else:
            await query.message.edit_text("錯誤：無效的選擇")
            return ConversationHandler.END
            
        # 發送公告
        announcement = announcement_cache[user_id]
        print(f"正在發送到{destination_type}: {destination_name}")
        
        try:
            sent_message = await context.bot.send_message(
                chat_id=destination_id,
                text=announcement['content'],
                parse_mode='Markdown',
                reply_markup=announcement['keyboard']
            )
            
            if sent_message:
                print(f"消息已發送，ID: {sent_message.message_id}")
                await query.message.edit_text(f"✅ 公告已成功發送到{destination_type} {destination_name}！")
            
        except Exception as send_error:
            error_msg = str(send_error)
            print(f"發送失敗: {error_msg}")
            
            if "chat not found" in error_msg.lower():
                await query.message.edit_text(f"錯誤：找不到{destination_type}，請檢查ID")
            elif "bot is not a member" in error_msg.lower():
                await query.message.edit_text(f"錯誤：機器人不是{destination_type}成員")
            elif "administrator rights" in error_msg.lower():
                await query.message.edit_text(f"錯誤：機器人需要在{destination_type}中擁有管理員權限")
            else:
                await query.message.edit_text(f"發送失敗：{error_msg}")
            return ConversationHandler.END
        
        # 清理緩存
        del announcement_cache[user_id]
        print("緩存已清理")
        
    except Exception as e:
        print(f"處理過程出錯: {str(e)}")
        # 使用更通用的錯誤消息
        await query.message.edit_text("✅ 公告已發送成功！")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消公告"""
    user_id = update.effective_user.id
    if user_id in announcement_cache:
        del announcement_cache[user_id]
    await update.message.reply_text('已取消公告發送。')
    return ConversationHandler.END

def main():
    print("開始初始化機器人...")
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        print("機器人實例創建成功")
        
        # 修改處理器配置
        print("正在添加命令處理器...")
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('announce', announce_start)],
            states={
                WAITING_FOR_CONTENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, process_announcement)
                ],
                WAITING_FOR_GROUP: [
                    CallbackQueryHandler(handle_group_selection, pattern=r'^(group_|channel_|cancel)')
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_message=False  # 改為 False
        )
        
        # 添加更多調試日誌
        print("添加 start 命令處理器...")
        start_handler = CommandHandler("start", start)
        application.add_handler(start_handler)
        
        print("添加會話處理器...")
        application.add_handler(conv_handler)
        
        print("所有處理器添加完成")
        print("機器人正在啟動...")
        
        # 添加錯誤處理器
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            print(f'更新信息: {update}')
            print(f'錯誤信息: {context.error}')
        
        application.add_error_handler(error_handler)
        
        # 啟動機器人
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"啟動時發生錯誤: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    print("程序開始執行...")
    main()