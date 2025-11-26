from telebot import types

# دیکشنری مرکزی تمام دکمه‌ها
ALL_BUTTONS = {
    # دکمه‌های اصلی
    "start": types.InlineKeyboardButton("🏠 شروع", callback_data='show_start'),
    "instagram": types.InlineKeyboardButton("📸 اینستاگرام", callback_data='instagram_download'),
    "youtube": types.InlineKeyboardButton("🎥 یوتیوب", callback_data='youtube_download'),
    "other": types.InlineKeyboardButton("📱 سایر شبکه‌ها", callback_data='other_download'),
    "pay": types.InlineKeyboardButton("💰 حمایت مالی", callback_data='show_pay'),
    "help": types.InlineKeyboardButton("📖 راهنما", callback_data='show_help'),
    
    # دکمه‌های عملیاتی
    "back": types.InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main'),
}



def create_keyboard(button_keys, row_width=2):
    """
    ایجاد کیبورد دلخواه از دکمه‌های مرکزی
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    
    # فیلتر کردن دکمه‌های معتبر
    valid_buttons = []
    for key in button_keys:
        if key in ALL_BUTTONS:
            valid_buttons.append(ALL_BUTTONS[key])
        else:
            print(f"⚠️ هشدار: دکمه '{key}' پیدا نشد!")
    
    # چیدمان دکمه‌ها
    for i in range(0, len(valid_buttons), row_width):
        row = valid_buttons[i:i + row_width]
        markup.add(*row)
    
    return markup

# کیبوردهای از پیش تعریف شده (برای راحتی)
def create_main_menu():
    """منوی اصلی"""
    return create_keyboard(['instagram', 'youtube', 'other', 'pay', 'help'], row_width=2)

def create_instagram_menu():
    """منوی اینستاگرام"""
    return create_keyboard(['back', 'help', 'pay'], row_width=1)

def create_back_menu():
    """منوی ساده بازگشت"""
    return create_keyboard(['back'], row_width=1)
"""
------------------------------------------------------------------------------------------------------
"""

def create_main_keyboard():
    """
    کیبورد اصلی - همه دکمه‌ها به جز بازگشت
    دلیل: در صفحه اصلی هستیم، نیازی به دکمه بازگشت نداریم
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # دکمه‌های اصلی - ردیف اول
    btn_instagram = types.KeyboardButton("📸 دانلود از اینستاگرام")
    btn_youtube = types.KeyboardButton("🎥 دانلود از یوتیوب")
    
    # دکمه‌های اصلی - ردیف دوم  
    btn_other = types.KeyboardButton("📱 سایر شبکه‌ها")
    
    # دکمه‌های کمکی - ردیف سوم
    btn_help = types.KeyboardButton("📖 راهنما")
    btn_pay = types.KeyboardButton("💰 حمایت مالی")
    
    # چیدمان دکمه‌ها
    markup.add(btn_instagram, btn_youtube)  # ردیف اول
    markup.add(btn_other)                   # ردیف دوم
    markup.add(btn_help, btn_pay)           # ردیف سوم
    
    return markup

def create_back_only_keyboard():
    """
    کیبورد فقط با دکمه بازگشت
    دلیل: در صفحات راهنما و حمایت مالی، فقط می‌خوایم کاربر بتونه برگرده
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_back = types.KeyboardButton("🔙 بازگشت به منوی اصلی")
    markup.add(btn_back)
    return markup

def create_instagram_keyboard():
    """
    کیبورد مخصوص اینستاگرام - بازگشت + راهنما
    دلیل: وقتی کاربر تو بخش اینستاگرامه، ممکنه نیاز به راهنما داشته باشه
    ولی دیگه نیاز به دکمه‌های دیگر نیست
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_back = types.KeyboardButton("🔙 بازگشت به منوی اصلی")
    btn_help = types.KeyboardButton("📖 راهنما")
    
    markup.add(btn_back)
    markup.add(btn_help)
    
    return markup

