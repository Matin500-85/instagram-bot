
from pytube import YouTube
import logging
from utils.helpers import user_log
from keyboards import menu, keyboard

logger = logging.getLogger(__name__)

def download_youtube_video(url):
    """دانلود ویدیو یوتیوب با مدیریت خطا"""
    try:
        yt = YouTube(url)
        
        # گرفتن اطلاعات
        video_info = {
            'title': yt.title,
            'duration': yt.length,
            'views': yt.views,
            'author': yt.author
        }
        
        # انتخاب بهترین کیفیت
        stream = yt.streams.filter(
            progressive=True, 
            file_extension='mp4'
        ).order_by('resolution').desc().first()
        
        if not stream:
            stream = yt.streams.get_highest_resolution()
        
        return {
            'success': True,
            'video_info': video_info,
            'download_url': stream.url,
            'filesize': stream.filesize
        }
        
    except Exception as e:
        logger.error(f"خطا در دانلود یوتیوب: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def setup_youtube_handlers(bot):
    @bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
    def handle_youtube_link(message):
        # 🔥 اضافه کردن user_log
        user_log(message.from_user, f"ارسال لینک یوتیوب: {message.text[:30]}...")
        
        try:
            # اطلاع شروع پردازش
            processing_msg = bot.reply_to(message, "⏳ در حال پردازش لینک یوتیوب...")
            
            # دانلود
            result = download_youtube_video(message.text)
            
            if result['success']:
                # 🔥 لاگ موفقیت
                user_log(message.from_user, f"دانلود موفق یوتیوب: {result['video_info']['title'][:20]}...")
                
                bot.edit_message_text(
                    f"✅ **آماده برای دانلود!**\n\n"
                    f"📹 **{result['video_info']['title']}**\n"
                    f"⏱️ مدت: {result['video_info']['duration']} ثانیه\n"
                    f"👤 سازنده: {result['video_info']['author']}\n"
                    f"💾 حجم: {result['filesize'] // (1024*1024)} مگابایت",
                    message.chat.id,
                    processing_msg.message_id
                )
                
                # ارسال ویدیو
                bot.send_video(
                    message.chat.id,
                    result['download_url'],
                    caption=result['video_info']['title'],
                    reply_markup=keyboard(['back', 'pay'])
                )
            else:
                # 🔥 لاگ خطا
                user_log(message.from_user, f"خطا در دانلود یوتیوب: {result['error']}", 'error')
                
                bot.edit_message_text(
                    f"❌ **خطا در دانلود:** {result['error']}",
                    message.chat.id,
                    processing_msg.message_id,
                    reply_markup=keyboard(['back', 'help'])
                )
                
        except Exception as e:
            # 🔥 لاگ خطای سیستمی
            user_log(message.from_user, f"خطای سیستمی یوتیوب: {e}", 'error')
            bot.reply_to(message, f"❌ خطای سیستمی: {e}")

    # 🔥 هندلر دکمه یوتیوب با user_log
    @bot.message_handler(func=lambda message: message.text == "🎥 دانلود از یوتیوب")
    def handle_youtube_button(message):
        """وقتی کاربر روی دکمه یوتیوب کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه یوتیوب")
        
        bot.send_message(
            message.chat.id,
            "🎥 *وارد بخش یوتیوب شدید!*\n\n"
            "لطفاً لینک ویدیو یوتیوب رو ارسال کنید...\n\n"
            "🔗 مثال:\n"
            "https://www.youtube.com/watch?v=...\n"
            "https://youtu.be/...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back', 'help'])
        )

    # 🔥 هندلر callback یوتیوب با user_log
    @bot.callback_query_handler(func=lambda call: call.data == 'youtube_download')
    def handle_youtube_callback(call):
        user_log(call.from_user, "کلیک روی دکمه اینلاین یوتیوب")
        
        bot.send_message(
            call.message.chat.id,
            "🎥 *بخش یوتیوب*\n\n"
            "لطفاً لینک ویدیو یوتیوب رو ارسال کنید...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back', 'help'])
        )
        bot.answer_callback_query(call.id)
