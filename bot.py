import os
import logging
import instaloader
import telebot
import time

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن از متغیر محیطی می‌خونیم
TOKEN = "8501768865:AAEdy3p04gtoL9ih6zYEkpz7kG1VFcGeIN0"

if not TOKEN:
    logger.error("❌ توکن ربات پیدا نشد! مطمئن شوی BOT_TOKEN تنظیم شده")
    exit(1)

# ساخت ربات
bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader()

def extract_shortcode(instagram_url):
    """استخراج shortcode از لینک اینستاگرام"""
    try:
        if '/p/' in instagram_url:
            return instagram_url.split('/p/')[1].split('/')[0]
        elif '/reel/' in instagram_url:
            return instagram_url.split('/reel/')[1].split('/')[0]
        elif '/stories/' in instagram_url:
            parts = instagram_url.split('/stories/')[1].split('/')
            return parts[1] if len(parts) > 1 else None
        else:
            return None
    except Exception as e:
        logger.error(f"خطا در استخراج shortcode: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """پاسخ به دستور /start"""
    welcome_text = """
🤖 **ربات دانلود از اینستاگرام**

📸 **پست‌ها** | 🎥 **ریلیزها** | 📱 **استوری‌ها**

✨ فقط لینک پست اینستاگرام رو برام بفرست!
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    """پاسخ به دستور /help"""
    help_text = """
📖 **راهنما:**

1. لینک پست اینستاگرام رو کپی کن
2. برای ربات بفرست
3. منتظر دانلود باش!

🔗 **مثال لینک:**
https://www.instagram.com/p/Cxample123/
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_instagram_link(message):
    """مدیریت لینک‌های اینستاگرام"""
    user_message = message.text.strip()
    
    # بررسی اینکه پیام لینک اینستاگرام هست
    if 'instagram.com' not in user_message:
        bot.reply_to(message, "❌ لطفاً فقط لینک معتبر اینستاگرام ارسال کن!")
        return
    
    shortcode = extract_shortcode(user_message)
    if not shortcode:
        bot.reply_to(message, "❌ لینک معتبر نیست! مطمئن شو لینک رو درست کپی کردی")
        return
    
    # اطلاع به کاربر
    processing_msg = bot.reply_to(message, "⏳ در حال دانلود... لطفاً صبر کن")
    
    try:
        # دانلود پست
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # ایجاد پوشه موقت برای دانلود
        download_dir = f"temp_{shortcode}"
        os.makedirs(download_dir, exist_ok=True)
        
        # دانلود محتوا
        L.download_post(post, target=download_dir)
        
        # پیدا کردن فایل‌های دانلود شده
        files = os.listdir(download_dir)
        media_files = [f for f in files if f.endswith(('.mp4', '.jpg', '.jpeg'))]
        
        if not media_files:
            bot.reply_to(message, "❌ محتوایی برای دانلود پیدا نشد!")
            return
        
        # ارسال فایل‌ها به کاربر
        success_count = 0
        for media_file in media_files:
            file_path = os.path.join(download_dir, media_file)
            try:
                if media_file.endswith('.mp4'):
                    with open(file_path, 'rb') as f:
                        bot.send_video(message.chat.id, f, timeout=60)
                        success_count += 1
                else:
                    with open(file_path, 'rb') as f:
                        bot.send_photo(message.chat.id, f, timeout=60)
                        success_count += 1
                
                # تأثیر بین ارسال فایل‌ها
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"خطا در ارسال فایل {media_file}: {e}")
                continue
            finally:
                # پاک کردن فایل
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # پاک کردن پوشه
        if os.path.exists(download_dir):
            os.rmdir(download_dir)
        
        # اطلاع پایان کار
        if success_count > 0:
            bot.reply_to(message, f"✅ دانلود کامل شد! {success_count} فایل ارسال شد.")
        else:
            bot.reply_to(message, "❌ خطا در ارسال فایل‌ها!")
        
        # پاک کردن پیام "در حال دانلود"
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
            
    except Exception as e:
        logger.error(f"خطا در دانلود: {e}")
        error_msg = f"""
❌ خطا در دانلود!

🔍 **دلایل احتمالی:**
• پست خصوصی هست
• لینک معتبر نیست
• مشکل در اتصال به اینستاگرام

📝 مطمئن شو پست public هست و لینک رو درست کپی کردی!
        """
        bot.reply_to(message, error_msg)

if __name__ == "__main__":
    logger.info("🚀 ربات در حال راه‌اندازی...")
    print("=" * 50)
    print("🤖 ربات دانلود از اینستاگرام")
    print("📍 فعال روی Railway")
    print("=" * 50)
    
    try:
        bot.polling(none_stop=True, interval=2, timeout=30)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")

