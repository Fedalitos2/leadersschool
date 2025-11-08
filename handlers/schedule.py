# ============================================
# 🔹 handlers/schedule.py — раздел "Расписание"
# ============================================

from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.main_menu import main_menu
from data.languages import user_languages

# ==============================
# 📌 Роутер для раздела "Расписание"
# ==============================
router = Router()

# ==============================
# 🔘 Обработка кнопки "Расписание"
# ==============================
@router.callback_query(lambda c: c.data == "schedule")
async def schedule_handler(call: CallbackQuery):
    """
    Показывает расписание занятий на выбранном языке
    """
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")  # язык по умолчанию

    texts = {
        "ru": "🕒 <b>Расписание занятий:</b>\n\n"
              "🏠 <b>Медицинская помощь дома:</b>\n"
              "• Вторник, Четверг, Суббота\n"
              "• 14:00 - 17:00\n\n"
              
              "🌍 <b>Английский язык:</b>\n"
              "• Starter: ежедневно 8:00 - 9:30\n"
              "• Beginner: ежедневно 8:00 - 9:30\n"
              "• Elementary: ежедневно 8:30 - 10:00\n"
              "• Pre-Intermediate: ежедневно 10:00 - 12:00\n"
              "• Pre-Intermediate (девушки): ежедневно 14:00 - 16:00\n"
              "• Pre-Intermediate (юноши): ежедневно 16:00 - 18:00\n"
              "• Intermediate (юноши): ежедневно 16:00 - 20:00\n\n"
              
              "🔬 <b>Биология:</b>\n"
              "• Понедельник, Среда, Четверг\n"
              "• 14:30 - 16:00\n\n"
              
              "💻 <b>IT курсы:</b>\n"
              "• Утренние: Вторник, Четверг, Суббота 8:00 - 10:00\n"
              "• Дневные: Вторник, Четверг, Суббота 14:00 - 16:00\n\n"
              
              "🌍 <b>Русский язык:</b>\n"
              "• Утренние: ежедневно 8:00 - 10:00\n"
              "• Дневные: ежедневно 14:00 - 16:00\n\n"
              
              "🧮 <b>Математика:</b>\n"
              "• Ежедневно: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🌍 <b>Арабский язык:</b>\n"
              "• Вторник, Четверг, Суббота: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🎓 <b>Подготовка в Президентскую школу:</b>\n"
              "• Ежедневно: 8:00 - 12:00",

        "uz": "🕒 <b>Dars jadvali:</b>\n\n"
              "🏠 <b>Uy Hamshiralik:</b>\n"
              "• Seshanba, Payshanba, Shanba\n"
              "• 14:00 - 17:00\n\n"
              
              "🌍 <b>Ingliz tili:</b>\n"
              "• Starter: har kuni 8:00 - 9:30\n"
              "• Beginner: har kuni 8:00 - 9:30\n"
              "• Elementary: har kuni 8:30 - 10:00\n"
              "• Pre-Intermediate: har kuni 10:00 - 12:00\n"
              "• Pre-Intermediate (qizlar): har kuni 14:00 - 16:00\n"
              "• Pre-Intermediate (o'g'il bolalar): har kuni 16:00 - 18:00\n"
              "• Intermediate (o'g'il bolalar): har kuni 16:00 - 20:00\n\n"
              
              "🔬 <b>Biologiya:</b>\n"
              "• Dushanba, Chorshanba, Payshanba\n"
              "• 14:30 - 16:00\n\n"
              
              "💻 <b>IT kurslari:</b>\n"
              "• Ertalabki: Seshanba, Payshanba, Shanba 8:00 - 10:00\n"
              "• Tushki: Seshanba, Payshanba, Shanba 14:00 - 16:00\n\n"
              
              "🌍 <b>Rus tili:</b>\n"
              "• Ertalabki: har kuni 8:00 - 10:00\n"
              "• Tushki: har kuni 14:00 - 16:00\n\n"
              
              "🧮 <b>Matematika:</b>\n"
              "• Har kuni: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🌍 <b>Arab tili:</b>\n"
              "• Seshanba, Payshanba, Shanba: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🎓 <b>Prezident maktabiga tayyorlov:</b>\n"
              "• Har kuni: 8:00 - 12:00",

        "en": "🕒 <b>Schedule:</b>\n\n"
              "🏠 <b>Home Nursing:</b>\n"
              "• Tuesday, Thursday, Saturday\n"
              "• 14:00 - 17:00\n\n"
              
              "🌍 <b>English Language:</b>\n"
              "• Starter: daily 8:00 - 9:30\n"
              "• Beginner: daily 8:00 - 9:30\n"
              "• Elementary: daily 8:30 - 10:00\n"
              "• Pre-Intermediate: daily 10:00 - 12:00\n"
              "• Pre-Intermediate (girls): daily 14:00 - 16:00\n"
              "• Pre-Intermediate (boys): daily 16:00 - 18:00\n"
              "• Intermediate (boys): daily 16:00 - 20:00\n\n"
              
              "🔬 <b>Biology:</b>\n"
              "• Monday, Wednesday, Thursday\n"
              "• 14:30 - 16:00\n\n"
              
              "💻 <b>IT Courses:</b>\n"
              "• Morning: Tuesday, Thursday, Saturday 8:00 - 10:00\n"
              "• Afternoon: Tuesday, Thursday, Saturday 14:00 - 16:00\n\n"
              
              "🌍 <b>Russian Language:</b>\n"
              "• Morning: daily 8:00 - 10:00\n"
              "• Afternoon: daily 14:00 - 16:00\n\n"
              
              "🧮 <b>Mathematics:</b>\n"
              "• Daily: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🌍 <b>Arabic Language:</b>\n"
              "• Tuesday, Thursday, Saturday: 8:00 - 10:00, 10:00 - 12:00, 14:00 - 16:00\n\n"
              
              "🎓 <b>Presidential School Preparation:</b>\n"
              "• Daily: 8:00 - 12:00"
    }

    # Отправляем сообщение с текстом и главное меню
    await call.message.answer(texts[lang], reply_markup=main_menu(lang))
    await call.answer()  # убираем "часики"