# register.py - обновленная версия с отправкой в группу админов
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import main_menu
from keyboards.admin_buttons import admin_approve_buttons
from data.languages import user_languages
from data.db import save_application
from data.admins import ADMINS

# ID группы администраторов
ADMIN_GROUP_ID = -4931417098

router = Router()

# Состояния для регистрации
class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_course = State()
    waiting_for_phone = State()

# Тексты на разных языках
registration_texts = {
    "ru": {
        "start": "📝 <b>Запись на курсы:</b>\n\nПожалуйста, отправьте ваше ФИО:",
        "full_name_example": "Пример: Иван Иванов",
        "course": "🎓 <b>Выберите курс:</b>\n\n" + "\n".join([
            "• Медицинская помощь дома",
            "• Английский язык", 
            "• Биология",
            "• IT курсы",
            "• Русский язык",
            "• Математика",
            "• Арабский язык",
            "• Подготовка в Президентскую школу",
            "• Бухгалтерский учет",
            "• Графический дизайн",
            "• Кибербезопасность",
            "• Мобильная разработка",
            "• Веб-разработка",
            "• Психология",
            "• Маркетинг и продажи"
        ]),
        "phone": "📱 <b>Отправьте ваш номер телефона:</b>\n\nПример: +998901234567",
        "success": "✅ <b>Ваша заявка отправлена!</b>\n\nАдминистратор свяжется с вами в ближайшее время.\nНомер заявки: #{}\n\n📞 Для связи: {}"
    },
    "uz": {
        "start": "📝 <b>Kurslarga ro'yxatdan o'tish:</b>\n\nIltimos, ismingizni yuboring:",
        "full_name_example": "Namuna: Alisher Navoiy",
        "course": "🎓 <b>Kursni tanlang:</b>\n\n" + "\n".join([
            "• Uy Hamshiralik",
            "• Ingliz tili",
            "• Biologiya",
            "• IT kurslari",
            "• Rus tili",
            "• Matematika",
            "• Arab tili",
            "• Prezident maktabiga tayyorlov",
            "• Buxgalteriya hisobi",
            "• Grafik dizayn",
            "• Kiberxavfsizlik",
            "• Mobil dasturlash",
            "• Veb-dasturlash",
            "• Psixologiya",
            "• Marketing va savdo"
        ]),
        "phone": "📱 <b>Telefon raqamingizni yuboring:</b>\n\nNamuna: +998901234567",
        "success": "✅ <b>Arizangiz yuborildi!</b>\n\nAdministrator tez orada siz bilan bog'lanadi.\nAriza raqami: #{}\n\n📞 Bog'lanish uchun: {}"
    },
    "en": {
        "start": "📝 <b>Register for courses:</b>\n\nPlease send your full name:",
        "full_name_example": "Example: John Smith",
        "course": "🎓 <b>Choose a course:</b>\n\n" + "\n".join([
            "• Home Nursing",
            "• English Language",
            "• Biology",
            "• IT Courses",
            "• Russian Language",
            "• Mathematics",
            "• Arabic Language",
            "• Presidential School Preparation",
            "• Accounting",
            "• Graphic Design",
            "• Cybersecurity",
            "• Mobile Development",
            "• Web Development",
            "• Psychology",
            "• Marketing and Sales"
        ]),
        "phone": "📱 <b>Send your phone number:</b>\n\nExample: +998901234567",
        "success": "✅ <b>Your application has been sent!</b>\n\nAn administrator will contact you shortly.\nApplication number: #{}\n\n📞 For contact: {}"
    }
}

# ==============================
# 🔘 Обработка кнопки "Записаться"
# ==============================
@router.callback_query(lambda c: c.data == "register")
async def register_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "uz")

    text = registration_texts[lang]["start"]
    await call.message.answer(text)
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await call.answer()

# ==============================
# 🔘 Получение ФИО
# ==============================
@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "uz")
    
    text = registration_texts[lang]["course"]
    await message.answer(text)
    await state.set_state(RegistrationStates.waiting_for_course)

# ==============================
# 🔘 Получение курса
# ==============================
@router.message(RegistrationStates.waiting_for_course)
async def process_course(message: Message, state: FSMContext):
    await state.update_data(course=message.text)
    
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "uz")
    
    text = registration_texts[lang]["phone"]
    await message.answer(text)
    await state.set_state(RegistrationStates.waiting_for_phone)

# ==============================
# 🔘 Получение телефона и отправка заявки
# ==============================
@router.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "uz")
    
    full_name = user_data['full_name']
    course = user_data['course']
    phone = message.text

    # Сохраняем заявку в базу
    application_id = save_application(user_id, full_name, course, phone, lang)
    
    # Отправляем уведомление администраторам в группу
    admin_text = f"🆕 <b>✨ НОВАЯ ЗАЯВКА НА КУРС ✨</b>\n\n" \
                 f"👤 <b>ФИО:</b> {full_name}\n" \
                 f"📚 <b>Курс:</b> {course}\n" \
                 f"📱 <b>Телефон:</b> {phone}\n" \
                 f"🆔 <b>Telegram ID:</b> {user_id}\n" \
                 f"👤 <b>Username:</b> @{message.from_user.username if message.from_user.username else 'Нет'}\n" \
                 f"📋 <b>Номер заявки:</b> #{application_id}\n" \
                 f"🌍 <b>Язык:</b> {lang.upper()}"

    try:
        # Отправляем в группу админов с кнопками
        await message.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=admin_text,
            reply_markup=admin_approve_buttons(user_id, application_id, message.from_user.username)
        )
    except Exception as e:
        print(f"Ошибка отправки в группу админов: {e}")
        # Резервная отправка всем админам
        for admin_id in ADMINS:
            try:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    reply_markup=admin_approve_buttons(user_id, application_id, message.from_user.username)
                )
            except:
                pass

    # Подтверждение пользователю
    success_text = registration_texts[lang]["success"].format(application_id, message.from_user.full_name)
    await message.answer(success_text, reply_markup=main_menu(lang))
    await state.clear()