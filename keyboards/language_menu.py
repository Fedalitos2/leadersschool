# ============================================
# 🔹 keyboards/language_menu.py — меню выбора языка
# ============================================

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🌍 Клавиатура с выбором языка
def language_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
