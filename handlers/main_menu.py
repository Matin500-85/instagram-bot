import time
from telebot import types
from keyboards import create_main_menu, create_back_menu

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
        bot.reply_to(message, get_welcome_text2(), reply_markup=create_main_keyboard())

    @bot.message_handler(commands=['pay'])
    def send_pay(message):
        bot.reply_to(message, get_pay_text(), reply_markup=create_back_only_keyboard(), parse_mode='Markdown')

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, get_help_text(), reply_markup=create_back_only_keyboard(), parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: call.data in ['show_pay', 'show_help', 'back_to_main'])
    def handle_main_callbacks(call):
        if call.data == 'show_pay':
            bot.send_message(call.message.chat.id, get_pay_text(), 
                           reply_markup=create_back_only_keyboard(), parse_mode='Markdown')
        elif call.data == 'show_help':
            bot.send_message(call.message.chat.id, get_help_text(), 
                           reply_markup=create_back_only_keyboard(), parse_mode='Markdown')
        elif call.data == 'back_to_main':
            bot.send_message(call.message.chat.id, get_welcome_text(), parse_mode='Markdown')
            time.sleep(0.5)
            bot.send_message(call.message.chat.id, get_welcome_text2(), reply_markup=create_main_keyboard())
        
        bot.answer_callback_query(call.id)


