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

⚡️ **ویژگی‌ها:**
• دانلود عکس و ویدئو
• ارسال کپشن کامل
• اطلاعات پست (لایک، کاربر)
• پشتیبانی از پست‌های چندرسانه‌ای
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')
    time.sleep(0.5)
    welcome2 = """
در صورت بروز خطا با پشتیبانی در ارتباط باشید👇👇
@Matin500_85
    """
    bot.reply_to(message, welcome2)   

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
💡 **نکات:**
• فقط پست‌های public قابل دانلود هستند
• پست‌های خصوصی نیاز به لاگین دارند
• در صورت خطا، ۱۰ دقیقه صبر کنید
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_instagram_link(message):
    """مدیریت لینک‌های اینستاگرام"""
    user_message = message.text.strip()
    
    if 'instagram.com' not in user_message:
        bot.reply_to(message, "❌ لطفاً فقط لینک معتبر اینستاگرام ارسال کن!")
        return
    
    shortcode = extract_shortcode(user_message)
    if not shortcode:
        bot.reply_to(message, "❌ لینک معتبر نیست! مطمئن شو لینک رو درست کپی کردی")
        return
    
    processing_msg = bot.reply_to(message, "⏳ در حال دانلود... لطفاً صبر کن")
    
    try:
        # دانلود پست
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # ساخت کپشن پیشرفته (قبل از دانلود)
        try:
            if post.caption:
                caption = f"📝 {post.caption}\n\n👤 {post.owner_username}\n❤️ {post.likes} لایک"
            else:
                caption = f"👤 {post.owner_username}\n❤️ {post.likes} لایک"
            
            # محدودیت کاراکتر تلگرام
            caption = caption[:1024]
        except Exception as e:
            logger.error(f"خطا در خواندن کپشن: {e}")
            caption = "Instagram Post"
        
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
        for i, media_file in enumerate(media_files):
            file_path = os.path.join(download_dir, media_file)
            try:
                # فقط برای اولین فایل کپشن بفرست
                current_caption = caption if i == 0 else None
                
                if media_file.endswith('.mp4'):
                    with open(file_path, 'rb') as f:
                        bot.send_video(message.chat.id, f, 
                                     caption=current_caption,
                                     timeout=60)
                        success_count += 1
                else:
                    with open(file_path, 'rb') as f:
                        bot.send_photo(message.chat.id, f,
                                     caption=current_caption,
                                     timeout=60)
                        success_count += 1
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"خطا در ارسال فایل {media_file}: {e}")
                continue
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        if os.path.exists(download_dir):
            os.rmdir(download_dir)
# اطلاع پایان کار
        if success_count > 0:
            final_msg = f"✅ **دانلود کامل شد!**\n\n📦 **{success_count} فایل ارسال شد**\n👤 **@{post.owner_username}**\n❤️ **{post.likes} لایک**"
            bot.reply_to(message, final_msg, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ خطا در ارسال فایل‌ها!")
        
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
            
    except Exception as e:
        logger.error(f"خطا در دانلود: {e}")
        
        # پیام‌های کاربرپسند
        error_msg = "❌ خطا در دانلود! "
        error_str = str(e).lower()
        
        if "login" in error_str or "private" in error_str:
            error_msg += "این پست خصوصی هست"
        elif "blocked" in error_str or "rate" in error_str:
            error_msg += "محدودیت موقت! ۱۰ دقیقه صبر کن"
        elif "not found" in error_str:
            error_msg += "پست پیدا نشد"
        elif "429" in error_str:
            error_msg += "درخواست زیاد! کمی صبر کن"
        else:
            error_msg += "مطمئن شو پست public هست"
        
        bot.reply_to(message, error_msg)

if __name__ == "__main__":
    logger.info("🚀 ربات در حال راه‌اندازی...")
    print("=" * 50)
    print("🤖 ربات دانلود از اینستاگرام")
    print("📍 فعال روی Railway")
    print("⚡️ نسخه: پیشرفته با کپشن")
    print("=" * 50)
    
    try:
        bot.polling(none_stop=True, interval=2, timeout=30)
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")









