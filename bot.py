import os
import logging
import instaloader
import telebot
import time

# تنظیمات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن از متغیر محیطی Heroku بخونه
TOKEN = os.environ.get('BOT_TOKEN', '8501768865:AAEdy3p04gtoL9ih6zYEkpz7kG1VFcGeIN0')

bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader()

def extract_shortcode(instagram_url):
    try:
        if '/p/' in instagram_url:
            return instagram_url.split('/p/')[1].split('/')[0]
        elif '/reel/' in instagram_url:
            return instagram_url.split('/reel/')[1].split('/')[0]
        else:
            return None
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        '🤖 ربات دانلود از اینستاگرام\n\n'
        'لینک پست اینستاگرام رو برام بفرست تا محتواش رو برات دانلود کنم!',
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def download_instagram(message):
    user_message = message.text
    
    if 'instagram.com' not in user_message:
        bot.reply_to(message, '❌ لطفاً فقط لینک اینستاگرام ارسال کن!')
        return
    
    shortcode = extract_shortcode(user_message)
    if not shortcode:
        bot.reply_to(message, '❌ لینک معتبر نیست!')
        return
    
    try:
        msg = bot.reply_to(message, '⏳ در حال دانلود... لطفاً صبر کن')
        
        # دانلود پست
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # دانلود در پوشه موقت
        download_dir = f"temp_{shortcode}"
        L.download_post(post, target=download_dir)
        
        # پیدا کردن فایل‌های دانلود شده
        files = os.listdir(download_dir)
        media_files = [f for f in files if f.endswith(('.mp4', '.jpg', '.jpeg'))]
        
        if not media_files:
            bot.reply_to(message, '❌ فایلی برای دانلود پیدا نشد!')
            return
        
        # ارسال به کاربر
        for media_file in media_files:
            file_path = os.path.join(download_dir, media_file)
            try:
                if media_file.endswith('.mp4'):
                    with open(file_path, 'rb') as f:
                        bot.send_video(message.chat.id, f, timeout=60)
                else:
                    with open(file_path, 'rb') as f:
                        bot.send_photo(message.chat.id, f, timeout=60)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                continue
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        if os.path.exists(download_dir):
            os.rmdir(download_dir)
            
        bot.reply_to(message, '✅ دانلود کامل شد!')
        
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(message, f'❌ خطا در دانلود! مطمئن شو لینک عمومی هست.')

if __name__ == "__main__":
    print("🤖 ربات روی Heroku فعال شد...")
    bot.polling(none_stop=True)