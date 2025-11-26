from telebot import types

# ==================== مرجع دکمه‌های اینلاین ====================
INLINE_BUTTONS = {
    "start": types.InlineKeyboardButton("🏠 شروع", callback_data='show_start'),
    "instagram": types.InlineKeyboardButton("📸 اینستاگرام", callback_data='instagram_download'),
    "youtube": types.InlineKeyboardButton("🎥 یوتیوب", callback_data='youtube_download'), 
    "other": types.InlineKeyboardButton("📱 سایر شبکه‌ها", callback_data='other_download'),
    "pay": types.InlineKeyboardButton("💰 حمایت مالی", callback_data='show_pay'),
    "help": types.InlineKeyboardButton("📖 راهنما", callback_data='show_help'),
    "back": types.InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main'),
    "quick_download": types.InlineKeyboardButton("🚀 دانلود سریع", callback_data='quick_download'),
    "video_tutorial": types.InlineKeyboardButton("🎬 آموزش ویدیویی", callback_data='video_tutorial'),
    "support": types.InlineKeyboardButton("👨‍💻 پشتیبانی", url='https://t.me/Matin500_85'),
    "instagram_info": types.InlineKeyboardButton("📸 اینستاگرام", callback_data='instagram_info'),
    "youtube_info": types.InlineKeyboardButton("🎥 یوتیوب", callback_data='youtube_info'),
    "website": types.InlineKeyboardButton("🌐 وبسایت", url='https://example.com'),
}

# ==================== مرجع دکمه‌های ثابت ====================
REPLY_BUTTONS = {
    "instagram": types.KeyboardButton("📸 دانلود از اینستاگرام"),
    "youtube": types.KeyboardButton("🎥 دانلود از یوتیوب"),
    "other": types.KeyboardButton("📱 سایر شبکه‌ها"),
    "pay": types.KeyboardButton("💰 حمایت مالی"), 
    "help": types.KeyboardButton("📖 راهنما"),
    "back": types.KeyboardButton("🔙 بازگشت به منوی اصلی"),
    "refresh": types.KeyboardButton("🔄 بروزرسانی"),
    "settings": types.KeyboardButton("⚙️ تنظیمات"),
}

# ==================== تابع اصلی برای اینلاین ====================
def menu(button_keys, row_width=2):
    """
    ساخت کیبورد اینلاین از مرجع INLINE_BUTTONS
    
    Args:
        button_keys (list): لیست کلیدهای دکمه‌ها از INLINE_BUTTONS
        row_width (int): تعداد دکمه در هر ردیف (پیش‌فرض: ۲)
    
    Returns:
        types.InlineKeyboardMarkup: کیبورد اینلاین آماده
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    
    # پیدا کردن دکمه‌های معتبر
    valid_buttons = []
    for key in button_keys:
        if key in INLINE_BUTTONS:
            valid_buttons.append(INLINE_BUTTONS[key])
        else:
            print(f"⚠️ هشدار: دکمه اینلاین '{key}' پیدا نشد!")
    
    # چیدن دکمه‌ها در ردیف‌ها
    for i in range(0, len(valid_buttons), row_width):
        row = valid_buttons[i:i + row_width]
        markup.add(*row)
    
    return markup

# ==================== تابع اصلی برای ثابت ====================
def keyboard(button_keys, row_width=2):
    """
    ساخت کیبورد ثابت از مرجع REPLY_BUTTONS
    
    Args:
        button_keys (list): لیست کلیدهای دکمه‌ها از REPLY_BUTTONS  
        row_width (int): تعداد دکمه در هر ردیف (پیش‌فرض: ۲)
    
    Returns:
        types.ReplyKeyboardMarkup: کیبورد ثابت آماده
    """
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=row_width
    )
    
    # پیدا کردن دکمه‌های معتبر
    valid_buttons = []
    for key in button_keys:
        if key in REPLY_BUTTONS:
            valid_buttons.append(REPLY_BUTTONS[key])
        else:
            print(f"⚠️ هشدار: دکمه ثابت '{key}' پیدا نشد!")
    
    # چیدن دکمه‌ها در ردیف‌ها
    for i in range(0, len(valid_buttons), row_width):
        row = valid_buttons[i:i + row_width]
        markup.add(*row)
    
    return markup
