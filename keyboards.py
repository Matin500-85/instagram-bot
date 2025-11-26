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

