import os
import time
import logging
import telebot

# تنظیمات اولیه
from utils.helpers import setup_logging, user_log
from handlers.main_menu import setup_main_handlers
from handlers.instagram_downloader import setup_instagram_handlers


# توکن از متغیر محیطی می‌خونیم
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("❌ توکن ربات پیدا نشد! مطمئن شوی BOT_TOKEN تنظیم شده")
    exit(1)


# ساخت ربات
bot = telebot.TeleBot(TOKEN)

def main():
    """تابع اصلی اجرای ربات"""
    
    # تنظیم لاگینگ
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # تنظیم تمام هندلرها
    setup_main_handlers(bot)
    setup_instagram_handlers(bot)
    
    # هندلر برای دکمه‌های دیگر (برای آینده)
    @bot.callback_query_handler(func=lambda call: call.data in ['youtube_download', 'other_download'])
    def handle_coming_soon(call):
        bot.answer_callback_query(call.id, "⏳ به زودی فعال خواهد شد!", show_alert=True)
    
    # اجرای ربات
    logger.info("🚀 ربات در حال راه‌اندازی...")
    print("=" * 50)
    print("🤖 ربات دانلود چندمنظوره")
    print("📍 فعال روی Railway")
    print("⚡️ نسخه: سازمان‌یافته و ماژولار")
    print("=" * 50)

    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.polling(none_stop=True, interval=3, timeout=60)
        except Exception as error:
            logger.error(f"خطا در اجرای ربات: {error}")
            time.sleep(10)

if __name__ == "__main__":
    main()

