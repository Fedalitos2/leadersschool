# admin_buttons.py - yangi funksiyalar bilan takomillashtirilgan versiya
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_approve_buttons(user_id: int, application_id: int, username: str = ""):
    """Profil havolasi bilan chiroyli ariza tugmalari"""
    profile_link = f"https://t.me/{username}" if username else f"tg://user?id={user_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{user_id}_{application_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}_{application_id}")
        ],
        [
            InlineKeyboardButton(text="👤 Foydalanuvchi profili", url=profile_link),
            InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact_{user_id}")
        ],
        [
            InlineKeyboardButton(text="💬 Tez javob berish", callback_data=f"quick_answer_{user_id}"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_{application_id}")
        ]
    ])

def admin_question_buttons(user_id: int, question_id: int, username: str = ""):
    """Profil havolasi bilan chiroyli savol tugmalari"""
    profile_link = f"https://t.me/{username}" if username else f"tg://user?id={user_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Javob berish", callback_data=f"answer_question_{user_id}_{question_id}"),
            InlineKeyboardButton(text="✅ Javob berildi", callback_data=f"question_done_{question_id}")
        ],
        [
            InlineKeyboardButton(text="👤 Foydalanuvchi profili", url=profile_link),
            InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact_{user_id}")
        ],
        [
            InlineKeyboardButton(text="⚡ Tezkor javob", callback_data=f"quick_reply_{user_id}"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_question_{question_id}")
        ]
    ])

# 🔘 Добавляем кнопку рассылки в админ-панель
# ==============================
def admin_panel_buttons():
    """Обновленная админ-панель с кнопкой рассылки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📝 Arizalar", callback_data="admin_pending_apps")
        ],
        [
            InlineKeyboardButton(text="❓ Savollar", callback_data="admin_pending_questions"),
            InlineKeyboardButton(text="⭐ Fikrlar", callback_data="admin_reviews")
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_refresh"),
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="✖️ Yopish", callback_data="admin_close")
        ]
    ])

def admin_review_buttons(review_id: int):
    """Fikr-mulohazalarni boshqarish tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"admin_delete_review_{review_id}"),
            InlineKeyboardButton(text="👁️ Yashirish", callback_data=f"admin_hide_review_{review_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_reviews_stats"),
            InlineKeyboardButton(text="📋 Ro'yxat", callback_data="admin_reviews_list")
        ]
    ])
    
# admin_buttons.py - добавляем кнопки для рассылки

def admin_broadcast_buttons():
    """Клавиатура для управления рассылками"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Рассылка группам", callback_data="broadcast_groups")
    builder.button(text="👤 Рассылка пользователям", callback_data="broadcast_users")
    builder.button(text="🌐 Всем получателям", callback_data="create_broadcast")
    builder.button(text="📊 Статистика рассылок", callback_data="broadcast_stats")
    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def broadcast_confirmation_buttons():
    """Клавиатура для подтверждения рассылки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить рассылку", callback_data="confirm_broadcast")
    builder.button(text="❌ Отменить", callback_data="cancel_broadcast")
    builder.adjust(1)
    return builder.as_markup()