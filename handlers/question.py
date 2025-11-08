# ============================================
# 🔹 handlers/question.py — раздел вопросов
# ============================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import main_menu
from keyboards.admin_buttons import admin_question_buttons
from data.languages import user_languages
from data.db import save_question, update_question_status
from data.admins import ADMINS
from handlers.admin import notify_admins_new_question

ADMIN_GROUP_ID = -4931417098

router = Router()

# Состояния для вопроса
class QuestionStates(StatesGroup):
    waiting_for_question = State()

# Тексты на разных языках
question_texts = {
    "ru": {
        "start": "❓ <b>Задайте ваш вопрос:</b>\n\nОпишите подробно, что вас интересует, и администратор ответит вам в ближайшее время.",
        "success": "✅ <b>Ваш вопрос отправлен!</b>\n\nАдминистратор ответит вам в ближайшее время.\nНомер вопроса: #{}\n\n📞 Для связи: {}",
        "answer_received": "💬 <b>Ответ от администратора:</b>\n\n{}"
    },
    "uz": {
        "start": "❓ <b>Savolingizni yuboring:</b>\n\nQiziqtirgan mavzuni batafsil yozing, administrator tez orada javob beradi.",
        "success": "✅ <b>Savolingiz yuborildi!</b>\n\nAdministrator tez orada javob beradi.\nSavol raqami: #{}\n\n📞 Bog'lanish uchun: {}",
        "answer_received": "💬 <b>Administratordan javob:</b>\n\n{}"
    },
    "en": {
        "start": "❓ <b>Ask your question:</b>\n\nDescribe in detail what interests you, and the administrator will respond shortly.",
        "success": "✅ <b>Your question has been sent!</b>\n\nAn administrator will respond shortly.\nQuestion number: #{}\n\n📞 For contact: {}",
        "answer_received": "💬 <b>Answer from administrator:</b>\n\n{}"
    }
}

# ==============================
# 🔘 Кнопка "Задать вопрос"
# ==============================
@router.callback_query(lambda c: c.data == "ask_question")
async def ask_question_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "uz")

    text = question_texts[lang]["start"]
    await call.message.answer(text)
    await state.set_state(QuestionStates.waiting_for_question)
    await call.answer()

# ==============================
# 🔘 Получение вопроса
# ==============================
@router.message(QuestionStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "uz")
    question_text = message.text

    # Сохраняем вопрос в базу
    question_id = save_question(user_id, question_text, lang)
    
    # Уведомляем администраторов
    user_info = {
        'full_name': message.from_user.full_name,
        'question_text': question_text
    }
    await notify_admins_new_question(message.bot, question_id, user_info)

    # Отправляем администраторам
    admin_text = f"❓ <b>Yangi savol</b>\n\n" \
                 f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name}\n" \
                 f"🆔 <b>ID:</b> {user_id}\n" \
                 f"👤 <b>Username:</b> @{message.from_user.username if message.from_user.username else 'Yo\'q'}\n" \
                 f"📋 <b>Savol №:</b> {question_id}\n\n" \
                 f"💬 <b>Savol:</b>\n{question_text}"

    try:
        await message.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=admin_text,
            reply_markup=admin_question_buttons(user_id, question_id, message.from_user.username)
        )
    except Exception as e:
        print(f"Adminlarga jo'natishda xatolik: {e}")

    # Подтверждение пользователю
    user_text = question_texts[lang]["success"].format(question_id, message.from_user.full_name)
    await message.answer(user_text, reply_markup=main_menu(lang))
    await state.clear()