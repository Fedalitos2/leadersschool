# ============================================
# 🔹 handlers/contacts.py — раздел "Контакты"
# ============================================

from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.main_menu import main_menu
from data.languages import user_languages

# ==============================
# 📌 Роутер для раздела "Контакты"
# ==============================
router = Router()

# ==============================
# 🔘 Обработка кнопки "Контакты"
# ==============================
@router.callback_query(lambda c: c.data == "contacts")
async def contacts_handler(call: CallbackQuery):
    """
    Показывает контактную информацию учебного центра на выбранном языке
    """
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")  # язык по умолчанию

    texts = {
        "ru": "📞 <b>Контакты Учебного Центра:</b>\n\n"
              "📧 Email: leadersschool0101@gmail.com\n"
              "📱 Телефон: +998 94 452 45 52\n"
              "📍 Адрес: г. Корасув, вокруг Хокимията",
        "uz": "📞 <b>O'quv Markazi Kontaktlari:</b>\n\n"
              "📧 Email: leadersschool0101@gmail.com\n"
              "📱 Telefon: +998 94 452 45 52\n"
              "📍 Manzil: Qorasuv sh., Hokimiyati atrofi",
        "en": "📞 <b>Learning Center Contacts:</b>\n\n"
              "📧 Email: leadersschool0101@gmail.com\n"
              "📱 Phone: +998 94 452 45 52\n"
              "📍 Address: Qorasuv city, around the Hokimiyat"
    }

    # Отправляем сообщение с текстом и главное меню
    await call.message.answer(texts[lang], reply_markup=main_menu(lang))
    await call.answer()  # убираем "часики"