import time
from telebot import types
from keyboards import menu , keyboard
from utils.helpers import setup_logging, user_log

def get_welcome_text():
    return """
🤖 *ربات دانلود چندمنظوره*

📸 *از کجا می‌خوای دانلود کنی؟*

✨ **امکانات ربات:**
• دانلود از اینستاگرام (پست، ریلیز، استوری)
• دانلود از یوتیوب (به زودی...)
• دانلود از دیگر شبکه‌ها (به زودی...)

🎯 **ویژگی‌ها:**
• کیفیت اصلی
• کپشن کامل
• پشتیبانی از محتوای چندرسانه‌ای
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

1. یکی از گزینه‌ها رو انتخاب کن
2. لینک مورد نظر رو بفرست
3. منتظر دانلود باش!

🔗 *مثال لینک اینستاگرام:*
https://www.instagram.com/p/Cxample123/
    """



def setup_main_handlers(bot):
    """تنظیم هندلرهای منوی اصلی"""
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, get_welcome_text(), parse_mode='Markdown')
        time.sleep(0.5)
        bot.reply_to(message, get_welcome_text2(), reply_markup=keyboard(['instagram','youtube','pay','help']))

    @bot.message_handler(commands=['pay'])
    def send_pay(message):
        bot.reply_to(message, get_pay_text(), reply_markup=keyboard(['back']), parse_mode='Markdown')

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, get_help_text(), reply_markup=keyboard(['back']), parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: call.data in ['show_pay', 'show_help', 'back_to_main'])
    def handle_main_callbacks(call):
        if call.data == 'show_pay':
            bot.send_message(call.message.chat.id, get_pay_text(), 
                           reply_markup=keyboard(['back']), parse_mode='Markdown')
        elif call.data == 'show_help':
            bot.send_message(call.message.chat.id, get_help_text(), 
                           reply_markup=keyboard(['back']), parse_mode='Markdown')
        elif call.data == 'back_to_main':
            bot.send_message(call.message.chat.id, get_welcome_text(), parse_mode='Markdown')
            time.sleep(0.5)
            bot.send_message(call.message.chat.id, get_welcome_text2(), reply_markup=keyboard(['instagram','youtube','pay','help']))
        
        bot.answer_callback_query(call.id)

    @bot.message_handler(func=lambda message: message.text == "📸 دانلود از اینستاگرام")
    def handle_instagram_button(message):
        """وقتی کاربر روی دکمه اینستاگرام کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه اینستاگرام")
        
        bot.send_message(
            message.chat.id,
            "📸 *وارد بخش اینستاگرام شدید!*\n\n"
            "لطفاً لینک پست اینستاگرام رو ارسال کنید...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back', 'help'])  
        )
    
    @bot.message_handler(func=lambda message: message.text == "🎥 دانلود از یوتیوب")
    def handle_youtube_button(message):
        """وقتی کاربر روی دکمه یوتیوب کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه یوتیوب")
        
        bot.send_message(
            message.chat.id,
            "🎥 *بخش یوتیوب*\n\n"
            "به زودی فعال خواهد شد...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back'])
        )
    
    @bot.message_handler(func=lambda message: message.text == "📱 سایر شبکه‌ها")
    def handle_other_button(message):
        """وقتی کاربر روی دکمه سایر شبکه‌ها کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه سایر شبکه‌ها")
        
        bot.send_message(
            message.chat.id,
            "📱 *سایر شبکه‌های اجتماعی*\n\n"
            "به زودی فعال خواهد شد...",
            parse_mode='Markdown',
            reply_markup=keyboard(['back'])
        )
    
    @bot.message_handler(func=lambda message: message.text == "📖 راهنما")
    def handle_help_button(message):
        """وقتی کاربر روی دکمه راهنما کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه راهنما")
        
        bot.send_message(
            message.chat.id,
            get_help_text(),
            parse_mode='Markdown',
            reply_markup=keyboard(['instagram','back','pay'])
        )
    
    @bot.message_handler(func=lambda message: message.text == "💰 حمایت مالی")
    def handle_pay_button(message):
        """وقتی کاربر روی دکمه حمایت مالی کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه حمایت مالی")
        
        bot.send_message(
            message.chat.id,
            get_pay_text(),
            parse_mode='Markdown',
            reply_markup=keyboard(['back'])
        )
    
    
    @bot.message_handler(func=lambda message: message.text == "🔙 بازگشت به منوی اصلی")
    def handle_back_button(message):
        """وقتی کاربر روی دکمه بازگشت کلیک میکنه"""
        user_log(message.from_user, "کلیک روی دکمه بازگشت")
        
        bot.send_message(
            message.chat.id,
            "🔙 *به منوی اصلی بازگشتید!*",
            parse_mode='Markdown',
            reply_markup=keyboard(['instagram','youtube','pay','help'])
        )
        




