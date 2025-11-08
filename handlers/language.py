# ============================================
# 🔹 handlers/language.py — tilni o'zgartirish
# ============================================

from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.language_menu import language_menu
from keyboards.main_menu import main_menu
from data.languages import user_languages

router = Router()

# ==============================
# 🔘 Tilni o'zgartirish tugmasi
# ==============================
@router.callback_query(lambda c: c.data == "change_language")
async def change_language_handler(call: CallbackQuery):
    """
    Har qanday vaqt tilni o'zgartirish imkoniyati
    """
    text = "🌍 <b>Tilni tanlang / Выберите язык / Choose language:</b>"
    await call.message.answer(text, reply_markup=language_menu())
    await call.answer()

# ==============================
# 🔘 Yangi tilni tanlash
# ==============================
@router.callback_query(lambda c: c.data.startswith("lang_"))
async def language_selected_handler(call: CallbackQuery):
    """
    Yangi tilni tanlaganda
    """
    user_id = call.from_user.id
    data = call.data
    lang = data.split("_")[1]  # ru, uz, en
    
    # Tilni saqlash
    user_languages[user_id] = lang
    
    # Tasdiqlash xabari
    confirm_texts = {
        "ru": "✅ <b>Язык изменен на Русский!</b>\n\nВыберите нужный раздел:",
        "uz": "✅ <b>Til O'zbekchaga o'zgartirildi!</b>\n\nKerakli bo'limni tanlang:",
        "en": "✅ <b>Language changed to English!</b>\n\nChoose a section:"
    }
    
    await call.message.answer(confirm_texts[lang], reply_markup=main_menu(lang))
    await call.answer()