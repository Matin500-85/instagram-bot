import os
import logging
import instaloader
import telebot
import threading
import time
from telebot import types


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

# for control
execution_lock = threading.Lock()
is_processing= False

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


def create_main_menu(allowed_buttons=['start','pay','help']):
    """تابع مادر برای ساخت منوی اصلی"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons={
        "start" : types.InlineKeyboardButton("🏠 شروع", callback_data='show_start'),
        "pay" : types.InlineKeyboardButton("حمایت مالی 💰", callback_data='show_pay'),
        "help" : types.InlineKeyboardButton("📖 راهنما", callback_data='show_help')
    }
    for btn in allowed_buttons:
        if btn in buttons:
            markup.add(buttons[btn])
            
    return markup


def get_welcome_text1():
    return """
🤖 *ربات دانلود از اینستاگرام*

📸 *پست‌ها* | 🎥 *ریلیزها* | 📱 *استوری‌ها*

✨ فقط لینک پست اینستاگرام رو برام بفرست!

⚡️ *ویژگی‌ها:*
• دانلود عکس و ویدئو
• ارسال کپشن کامل
• اطلاعات پست (لایک، کاربر)
• پشتیبانی از پست‌های چندرسانه‌ای  
    """

def get_welcome_text2():
    return """
در صورت بروز خطا با پشتیبانی در ارتباط باشید👇👇
@Matin500_85
    """


def get_pay_text():
    return """
🎉 *از حمایت شما سپاسگزاریم!*  

ربات ما همواره با هدف ارائه خدمات رایگان توسعه یافته است. اگر تمایل دارید از ما حمایت مالی کنید، از لطف شما بی‌نهایت سپاسگزاریم.  

💳 *شماره کارت برای حمایت مالی:*  
`6104 3373 6462 1514`
(بانک ملت)

💰 *آدرس ولت (TRC-20):*
`UQDdZQ0Pbmm30Qb78pZ1Hct3Fuu4c0rEdcNwAlDqisBIb5cV`

✨ *هر مبلغی که مقدور باشید، ارزشمند است.*
    """


def get_help_text():
    return """
📖 *راهنما:*

1. لینک پست اینستاگرام رو کپی کن
2. برای ربات بفرست
3. منتظر دانلود باش!

🔗 *مثال لینک:*
https://www.instagram.com/p/Cxample123/
💡 *نکات:*
• فقط پست‌های public قابل دانلود هستند
• پست‌های خصوصی نیاز به لاگین دارند
• در صورت خطا، ۱۰ دقیقه صبر کنید
    """


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """پاسخ به دستور /start"""
    bot.reply_to(message, get_welcome_text1(), parse_mode='Markdown')
    time.sleep(0.5)
    bot.reply_to(message, get_welcome_text2(), reply_markup=create_main_menu(['pay','help']))   


@bot.message_handler(commands=['pay'])
def send_pay(message):
    """پاسخ به دستور /pay"""
    bot.reply_to(message, get_pay_text(), reply_markup=create_main_menu(['start','help']), parse_mode='Markdown')
    
@bot.message_handler(commands=['help'])
def send_help(message):
    """پاسخ به دستور /help"""
    bot.reply_to(message, get_help_text(), reply_markup=create_main_menu(['start','pay']), parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_clicks(call):
    if call.data == 'show_start':
        # پیام اول
        bot.send_message(call.message.chat.id, get_welcome_text1(), parse_mode='Markdown')
        # صبر نیم ثانیه
        time.sleep(0.5)
        # پیام دوم با دکمه‌ها
        bot.send_message(
            call.message.chat.id, 
            get_welcome_text2(), 
            reply_markup=create_main_menu(['pay','help'])
        )
    elif call.data == 'show_pay':
        bot.send_message(call.message.chat.id, get_pay_text(), reply_markup=create_main_menu(['start','help']), parse_mode='Markdown')
    elif call.data == 'show_help':
        bot.send_message(call.message.chat.id, get_help_text(), reply_markup=create_main_menu(['start','pay']), parse_mode='Markdown')
    
    bot.answer_callback_query(call.id)


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
        bot.remove_webhook()
        time.sleep(1)
        bot.polling(none_stop=True, interval=2, timeout=30 , skip_pending=True )
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")























