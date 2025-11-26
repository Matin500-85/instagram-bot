import os
import logging
import re
import time
import random
import shutil
from collections import defaultdict

import instaloader
from keyboards import menu, keyboard
from telebot import types
from utils.helpers import setup_logging, user_log
from utils.message_router import route_message_by_content

logger = logging.getLogger(__name__)



USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]


L = instaloader.Instaloader(
    user_agent=random.choice(USER_AGENTS), # انتخاب تصادفی User-Agent
    request_timeout=60,                   # timeout بیشتر
    max_connection_attempts=2,            # تعداد تلاش کمتر
    download_comments=False,              # عدم دانلود کامنت‌ها
    save_metadata=False,                  # عدم ذخیره متادیتا
    post_metadata_txt_pattern="",         # غیرفعال کردن ذخیره متادیتا
    compress_json=False                   # غیرفعال کردن فشرده‌سازی
)
L.sleep = True



def get_instagram_instructions():
    return """
📸 *دانلود از اینستاگرام*

✨ **پشتیبانی از:**
• پست‌های عکس/ویدئو
• ریلیزها (Reels)  
• استوری‌ها (Stories)

🔗 **کافیه لینک رو بفرستی:**
https://www.instagram.com/p/Cxample123/
https://www.instagram.com/reel/Cxample123/
https://www.instagram.com/stories/username/123456789/

⚠️ **نکات:**
• فقط پست‌های public قابل دانلود هستند
• برای استوری‌های خصوصی نیاز به لاگین است
    """


# for control
processing_users = set()
user_requests= defaultdict(list)

def check_rate_limit(user_id, limit=3, window=60):
    current_time = time.time()
    
    # فقط درخواست‌های کاربر فعلی
    user_requests[user_id] = [
        t for t in user_requests[user_id] 
        if current_time - t < window
    ]
    
    if len(user_requests[user_id]) >= limit:
        return False
    
    user_requests[user_id].append(current_time)
    return True


def is_valid_instagram_url(url):
    """بررسی معتبر بودن لینک اینستاگرام"""
    pattern = r'^https?://(www\.)?instagram\.com/(p|reel|stories)/[a-zA-Z0-9_\-./?=]+$'
    return bool(re.match(pattern, url.strip()))



def extract_shortcode(instagram_url):
    """استخراج shortcode از لینک اینستاگرام - با پشتیبانی از استوری"""
    try:
        url = instagram_url.strip()
        
        # استخراج بر اساس نوع لینک
        if '/p/' in url:
            shortcode = url.split('/p/')[1].split('/')[0].split('?')[0]
        elif '/reel/' in url:
            shortcode = url.split('/reel/')[1].split('/')[0].split('?')[0]
        elif '/stories/' in url:
            # برای استوری: username/timestamp/
            parts = url.split('/stories/')[1].split('/')
            if len(parts) >= 2:
                shortcode = parts[1]  # timestamp part
            else:
                return None
        else:
            return None
        
        # اعتبارسنجی shortcode استخراج شده
        if shortcode and re.match(r'^[a-zA-Z0-9_-]{5,50}$', shortcode):
            return shortcode
        else:
            return None
            
    except Exception as e:
        logger.error(f"خطا در استخراج shortcode: {e}")
        return None


def setup_instagram_handlers(bot):
    """تنظیم هندلرهای مربوط به اینستاگرام"""
    @bot.callback_query_handler(func=lambda call: call.data == 'instagram_download')
    def handle_instagram_callback(call):
        """وقتی کاربر روی دکمه اینستاگرام کلیک می‌کند"""
        bot.send_message(call.message.chat.id, get_instagram_instructions(), 
                       reply_markup=keyboard(['help','back']), parse_mode='Markdown')
        bot.answer_callback_query(call.id)


    @bot.message_handler(func=lambda message: route_message_by_content(message) == 'instagram_link' )
    def handle_instagram_link(message):
        """مدیریت لینک‌های اینستاگرام"""
        user_id = message.from_user.id
        
        # چک کن اگر کاربر در حال پردازش هست
        if user_id in processing_users:
            bot.reply_to(message, "⏳ در حال پردازش درخواست قبلی شما... لطفاً صبر کنید")
            return
        # کاربر رو به لیست اضافه کن
        processing_users.add(user_id)
        
        try:
            user = message.from_user
            user_log(user, f"ارسال لینک: {message.text[:30]}...")

            user_message = message.text.strip()

            if not is_valid_instagram_url(user_message):
                user_log(user, "ارسال لینک غیر اینستاگرام", 'warning')
                bot.reply_to(message, "❌ لطفاً فقط لینک معتبر اینستاگرام ارسال کن!" ,reply_markup=keyboard(['help','back']))
                return

            if not check_rate_limit(user_id, limit=3, window=60):
                user_log(user, "محدودیت نرخ درخواست", 'warning')
                bot.reply_to(message, "🚫 تعداد درخواست‌های شما زیاد است! لطفاً ۱ دقیقه صبر کنید.",reply_markup=keyboard(['back']))
                return


            shortcode = extract_shortcode(user_message)
            if not shortcode:
                user_log(user, "لینک معتبر نیست", 'warning')
                bot.reply_to(message, "❌ لینک معتبر نیست! مطمئن شو لینک رو درست کپی کردی", reply_markup=keyboard(['help','back']))
                return

            processing_msg = bot.reply_to(message, "⏳ در حال دانلود... لطفاً صبر کن")
            user_log(user, f"شروع دانلود برای shortcode: {shortcode}")

            # ✅ تاخیر تصادفی برای جلوگیری از تشخیص ربات
            delay = random.randint(2, 5)  # 2 تا 5 ثانیه تاخیر
            time.sleep(delay)
            
            # ✅ تغییر User-Agent برای هر درخواست
            L.context.user_agent = random.choice(USER_AGENTS)

            
            
        finally:
            # پاک‌سازی پوشه موقت در صورت وجود
            try:
                if 'download_dir' in locals() and os.path.exists(download_dir):
                    shutil.rmtree(download_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"خطا در پاک‌سازی پوشه: {e}")

            # کاربر رو از لیست حذف کن حتی اگر خطا اتفاق افتاد
            processing_users.discard(user_id)

        try:
            # دانلود پست
            try:
                post = instaloader.Post.from_shortcode(L.context, shortcode)
            except instaloader.exceptions.PrivateError:
                # برای استوری‌ها پیام متفاوت بده
                if '/stories/' in user_message:
                    bot.reply_to(message, "❌ این استوری خصوصی است یا نیاز به لاگین دارد" , reply_markup=keyboard(['back']))
                else:
                    bot.reply_to(message, "❌ این پست خصوصی است و قابل دانلود نیست" , reply_markup=keyboard(['back']))
                return
            except instaloader.exceptions.QueryReturnedNotFoundException:
                bot.reply_to(message, "❌ پست پیدا نشد! ممکنه حذف شده باشه" , reply_markup=keyboard(['back']))
                return
            except instaloader.exceptions.ConnectionException:
                bot.reply_to(message, "🔌 مشکل اتصال به اینستاگرام! لطفاً دوباره تلاش کن", reply_markup=keyboard(['back']))
                return
            except Exception as e:
                user_log(message.from_user, f"خطای ناشناخته instaloader: {e}", 'error')
                bot.reply_to(message, "❌ خطا در دریافت اطلاعات پست", reply_markup=keyboard(['back']))
                return
        
            # چک کردن اگر استوری هست
            is_story = '/stories/' in user_message
            if is_story:
                # برای استوری‌ها پیام متفاوت بدیم
                bot.edit_message_text("📱 در حال دانلود استوری...", 
                                    message.chat.id, processing_msg.message_id)


            
            # ساخت کپشن پیشرفته (قبل از دانلود)
            try:
                if post.caption:
                    trimmed_caption=post.caption[:960]
                    caption = f"📝 {trimmed_caption}\n\n👤 {post.owner_username}\n❤️ {post.likes} لایک"
                else:
                    caption = f"👤 {post.owner_username}\n❤️ {post.likes} لایک"
                
                # محدودیت کاراکتر تلگرام
                caption = caption[:1024]
            except Exception as e:
                logger.error(f"خطا در خواندن کپشن: {e}")
                caption = "Instagram Post"
            
            # ایجاد پوشه موقت برای دانلود
            download_dir = f"temp_{shortcode}_{message.from_user.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            # دانلود محتوا
            L.download_post(post, target=download_dir)
            
            # پیدا کردن فایل‌های دانلود شده
            files = os.listdir(download_dir)
            video_files = [f for f in files if f.endswith('.mp4')]
            image_files = [f for f in files if f.endswith(('.jpg', '.jpeg'))]
            media_files = video_files + image_files
            
            if not media_files:
                bot.reply_to(message, "❌ محتوایی برای دانلود پیدا نشد!", reply_markup=keyboard(['help','back']))
                return

            # محدودیت حجم و تعداد فایل - اضافه شده
            MAX_FILE_SIZE = 80 * 1024 * 1024  # 50 مگابایت
            MAX_FILE_COUNT = 10
            
            total_size = 0
            for file in media_files:
                file_path = os.path.join(download_dir, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            
            if total_size > MAX_FILE_SIZE:
                bot.reply_to(message, "❌ حجم فایل بسیار بزرگ است! (بیشتر از 80MB)" , reply_markup=keyboard(['back']))
                shutil.rmtree(download_dir)
                return
            
            if len(media_files) > MAX_FILE_COUNT:
                bot.reply_to(message, "❌ تعداد فایل‌ها بسیار زیاد است! (بیشتر از 10 فایل)" , reply_markup=keyboard(['back']))
                shutil.rmtree(download_dir)
                return

            
            # ارسال فایل‌ها به کاربر
            success_count = 0
            for i, media_file in enumerate(media_files):
                file_path = os.path.join(download_dir, media_file)
                try:
                    # فقط برای اولین فایل کپشن بفرست
                    current_caption = caption if i == 0 else None

                    if (media_file.endswith(('.jpg','.jpeg')) and media_file.replace('.jpg','.mp4').replace('.jpeg','.mp4') in video_files):
                        current_caption="🏞کاور ویدیو"
                    
                    if media_file.endswith('.mp4'):
                        with open(file_path, 'rb') as f:
                            bot.send_video(message.chat.id, f, 
                                        caption=current_caption,
                                        parse_mode=None,
                                        reply_markup=menu(['pay']),
                                        timeout=60)
                            success_count += 1
                    else:
                        with open(file_path, 'rb') as f:
                            bot.send_photo(message.chat.id, f,
                                        caption=current_caption,
                                        parse_mode=None,
                                        reply_markup=keyboard(['pay','back']),
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
                shutil.rmtree(download_dir)
                
            # اطلاع پایان کار
            if success_count > 0:
                is_story = '/stories/' in user_message
                if is_story:
                    user_log(user, f"دانلود موفق: {success_count} فایل برای استوری {post.owner_username}")
                    final_msg = f"✅ **دانلود استوری کامل شد!**\n\n📦 **{success_count} فایل ارسال شد**\n👤 **@{post.owner_username}**"
                else:
                    user_log(user, f"دانلود موفق: {success_count} فایل برای پست {post.owner_username}")
                    final_msg = f"✅ **دانلود کامل شد!**\n\n📦 **{success_count} فایل ارسال شد**\n👤 **@{post.owner_username}**\n❤️ **{post.likes} لایک**"
                
                bot.reply_to(message, final_msg, parse_mode='Markdown',reply_markup=keyboard(['pay','back']),)
            else:
                user_log(user, "هیچ فایلی ارسال نشد", 'error')
                bot.reply_to(message, "❌ خطا در ارسال فایل‌ها!",reply_markup=keyboard(['back']),)
            
            
                
        except Exception as e:
            user_log(user, f"خطا در دانلود: {str(e)}", 'error')
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
            
            bot.reply_to(message, error_msg,reply_markup=keyboard(['help','back','pay']),)
            
        finally:
            try:
                bot.delete_message(message.chat.id, processing_msg.message_id)
            except:
                pass






