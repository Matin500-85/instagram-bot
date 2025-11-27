
import yt_dlp
import logging
from utils.helpers import user_log
from keyboards import menu, keyboard

logger = logging.getLogger(__name__)

def download_youtube_video(url):
    """دانلود ویدیو یوتیوب با yt-dlp"""
    try:
        # تنظیمات yt-dlp
        ydl_opts = {
            'format': 'best[height<=720]',  # حداکثر 720p
            'quiet': True,                  # غیرفعال کردن لاگ‌های داخلی
            'no_warnings': True,            # غیرفعال کردن اخطارها
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # دریافت اطلاعات ویدیو بدون دانلود
            info = ydl.extract_info(url, download=False)
            
            video_info = {
                'title': info.get('title', 'بدون عنوان'),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'author': info.get('uploader', 'ناشناس')
            }
            
            # بهترین لینک دانلود
            download_url = info['url']
            filesize = info.get('filesize', 0) or info.get('filesize_approx', 0)
            
            return {
                'success': True,
                'video_info': video_info,
                'download_url': download_url,
                'filesize': filesize
            }
            
    except Exception as e:
        logger.error(f"خطا در دانلود یوتیوب: {e}")
        
        # پیام‌های خطای کاربرپسند
        error_msg = str(e).lower()
        if 'unable to download webpage' in error_msg:
            user_error = "لینک معتبر نیست یا ویدیو حذف شده"
        elif 'video unavailable' in error_msg:
            user_error = "ویدیو در دسترس نیست"
        elif 'private video' in error_msg:
            user_error = "این ویدیو خصوصی است"
        elif 'age restricted' in error_msg:
            user_error = "این ویدیو محدودیت سنی دارد"
        else:
            user_error = f"خطا در دریافت ویدیو: {str(e)[:100]}"
        
        return {
            'success': False,
            'error': user_error
        }

def setup_youtube_handlers(bot):
    @bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
    def handle_youtube_link(message):
        user_log(message.from_user, f"ارسال لینک یوتیوب: {message.text[:30]}...")
        
        try:
            processing_msg = bot.reply_to(message, "⏳ در حال پردازش لینک یوتیوب...")
            
            result = download_youtube_video(message.text)
            
            if result['success']:
                user_log(message.from_user, f"دانلود موفق یوتیوب: {result['video_info']['title'][:20]}...")
                
                # فرمت کردن مدت زمان
                duration = result['video_info']['duration']
                if duration > 3600:
                    duration_str = f"{duration//3600}:{(duration%3600)//60:02d}:{duration%60:02d}"
                else:
                    duration_str = f"{duration//60}:{duration%60:02d}"
                
                # فرمت کردن حجم فایل
                filesize_mb = result['filesize'] // (1024 * 1024) if result['filesize'] else 0
                
                bot.edit_message_text(
                    f"✅ **آماده برای دانلود!**\n\n"
                    f"📹 **{result['video_info']['title']}**\n"
                    f"⏱️ مدت: {duration_str}\n"
                    f"👁️ بازدید: {result['video_info']['views']:,}\n"
                    f"👤 سازنده: {result['video_info']['author']}\n"
                    f"💾 حجم: {filesize_mb} مگابایت",
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode='Markdown'
                )
                
                # ارسال ویدیو
                bot.send_video(
                    message.chat.id,
                    result['download_url'],
                    caption=result['video_info']['title'],
                    reply_markup=keyboard(['back', 'pay']),
                    timeout=60
                )
                
            else:
                user_log(message.from_user, f"خطا در دانلود یوتیوب: {result['error']}", 'error')
                
                bot.edit_message_text(
                    f"❌ **{result['error']}**\n\n"
                    "لطفاً لینک معتبر یوتیوب ارسال کنید:",
                    message.chat.id,
                    processing_msg.message_id,
                    reply_markup=keyboard(['back', 'help'])
                )
                
        except Exception as e:
            user_log(message.from_user, f"خطای سیستمی یوتیوب: {e}", 'error')
            bot.reply_to(message, f"❌ خطای سیستمی: {str(e)[:100]}")

    @bot.message_handler(func=lambda message: message.text == "🎥 دانلود از یوتیوب")
    def handle_youtube_button(message):
        user_log(message.from_user, "کلیک روی دکمه یوتیوب")
        
        bot.send_message(
            message.chat.id,
            "🎥 *وارد بخش یوتیوب شدید!*\n\n"
            "لطفاً لینک ویدیو یوتیوب رو ارسال کنید...\n\n"
            "🔗 **مثال‌ها:**\n"
            "• https://www.youtube.com/watch?v=...\n"
            "• https://youtu.be/...\n"
            "• https://www.youtube.com/shorts/...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back', 'help'])
        )

