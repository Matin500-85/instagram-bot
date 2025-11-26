import re

def route_message_by_content(message):
    """مسیریابی پیام بر اساس محتوا"""
    
    text = message.text
    
    # اگر پیغام متنی نداره (مثلاً عکس یا استیکر)
    if not text:
        return 'unknown'
    
    text = text.lower().strip()
    
    # بررسی لینک‌های اینستاگرام
    instagram_patterns = [
        r'https?://(www\.)?instagram\.com/(p|reel|stories)/',
        r'https?://(www\.)?instagr\.am/(p|reel|stories)/'
    ]
    
    if any(re.search(pattern, text) for pattern in instagram_patterns):
        return 'instagram_link'
    
    # بررسی لینک‌های یوتیوب
    youtube_patterns = [
        r'https?://(www\.)?youtube\.com/',
        r'https?://(www\.)?youtu\.be/'
    ]
    
    if any(re.search(pattern, text) for pattern in youtube_patterns):
        return 'youtube_link'
    
    return 'unknown'  # برای همه موارد دیگه
