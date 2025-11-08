# ============================================
# 🔹 keyboards/reviews_menu.py — меню для системы отзывов
# ============================================

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def reviews_menu(lang: str = "ru", is_admin: bool = False):
    """
    Меню системы отзывов
    """
    if lang == "ru":
        keyboard = [
            [InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data="leave_review")],
            [InlineKeyboardButton(text="👀 Посмотреть отзывы", callback_data="view_reviews")]
        ]
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="📊 Статистика отзывов", callback_data="reviews_stats")])
        keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_main")])
        
    elif lang == "uz":
        keyboard = [
            [InlineKeyboardButton(text="⭐ Fikr qoldirish", callback_data="leave_review")],
            [InlineKeyboardButton(text="👀 Fikrlarni ko'rish", callback_data="view_reviews")]
        ]
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="📊 Fikrlar statistikasi", callback_data="reviews_stats")])
        keyboard.append([InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_main")])
        
    else:  # en
        keyboard = [
            [InlineKeyboardButton(text="⭐ Leave review", callback_data="leave_review")],
            [InlineKeyboardButton(text="👀 View reviews", callback_data="view_reviews")]
        ]
        if is_admin:
            keyboard.append([InlineKeyboardButton(text="📊 Reviews stats", callback_data="reviews_stats")])
        keyboard.append([InlineKeyboardButton(text="🏠 Main menu", callback_data="back_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_reviews_buttons(review_id: int):
    """
    Кнопки для админов к отзывам
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_review_{review_id}"),
            InlineKeyboardButton(text="👁️ Скрыть", callback_data=f"admin_hide_review_{review_id}")
        ]
    ])