# ============================================
# 🔹 handlers/reviews.py — улучшенная система отзывов
# ============================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import main_menu
from keyboards.reviews_menu import reviews_menu, admin_reviews_buttons
from data.languages import user_languages
from data.db import save_review, get_reviews, delete_review, get_review_stats, hide_review
from data.admins import is_admin
from data.admins import ADMINS

router = Router()

# Состояния для отзыва
class ReviewStates(StatesGroup):
    waiting_for_review = State()
    waiting_for_rating = State()

# Тексты на разных языках
review_texts = {
    "ru": {
        "start": "⭐ <b>Оставьте отзыв о нашем учебном центре!</b>\n\n"
                "Пожалуйста, оцените нас от 1 до 5 звезд:",
        "ask_text": "📝 <b>Напишите ваш отзыв:</b>\n\n"
                   "Расскажите о вашем опыте обучения. Что вам понравилось? "
                   "Что можно улучшить?",
        "success": "✅ <b>Спасибо за ваш отзыв!</b>\n\n"
                  "Ваше мнение очень важно для нас и поможет стать лучше.\n\n"
                  "⭐ Оценка: {}/5\n"
                  "📝 Отзыв: {}",
        "all_reviews": "💬 <b>Все отзывы студентов:</b>\n\n",
        "no_reviews": "📝 <b>Отзывов пока нет</b>\n\n"
                     "Будьте первым, кто оставит отзыв!",
        "review_deleted": "🗑️ <b>Отзыв удален</b>",
        "stats": "📊 <b>Статистика отзывов:</b>\n\n"
                "⭐ Средняя оценка: {:.1f}/5\n"
                "📝 Всего отзывов: {}\n"
                "🎯 Распределение:\n{}",
        "not_admin": "⛔ <b>У вас нет прав администратора!</b>"
    },
    "uz": {
        "start": "⭐ <b>O'quv markazimiz haqida fikringizni yozing!</b>\n\n"
                "Iltimos, bizni 1 dan 5 yulduzgacha baholang:",
        "ask_text": "📝 <b>Fikringizni yozing:</b>\n\n"
                   "O'qish tajribangiz haqida hikoya qiling. Nima yoqdi? "
                   "Nimani yaxshilash mumkin?",
        "success": "✅ <b>Fikringiz uchun rahmat!</b>\n\n"
                  "Sizning fikringiz biz uchun juda muhim va yaxshilanishga yordam beradi.\n\n"
                  "⭐ Baho: {}/5\n"
                  "📝 Fikr: {}",
        "all_reviews": "💬 <b>Barcha talabalar fikrlari:</b>\n\n",
        "no_reviews": "📝 <b>Hozircha fikrlar yo'q</b>\n\n"
                     "Fikr qoldirgan birinchi bo'ling!",
        "review_deleted": "🗑️ <b>Fikr o'chirildi</b>",
        "stats": "📊 <b>Fikrlar statistikasi:</b>\n\n"
                "⭐ O'rtacha baho: {:.1f}/5\n"
                "📝 Jami fikrlar: {}\n"
                "🎯 Taqsimot:\n{}",
        "not_admin": "⛔ <b>Sizda administrator huquqlari yo'q!</b>"
    },
    "en": {
        "start": "⭐ <b>Leave a review about our learning center!</b>\n\n"
                "Please rate us from 1 to 5 stars:",
        "ask_text": "📝 <b>Write your review:</b>\n\n"
                   "Tell us about your learning experience. What did you like? "
                   "What can be improved?",
        "success": "✅ <b>Thank you for your review!</b>\n\n"
                  "Your opinion is very important to us and will help us improve.\n\n"
                  "⭐ Rating: {}/5\n"
                  "📝 Review: {}",
        "all_reviews": "💬 <b>All student reviews:</b>\n\n",
        "no_reviews": "📝 <b>No reviews yet</b>\n\n"
                     "Be the first to leave a review!",
        "review_deleted": "🗑️ <b>Review deleted</b>",
        "stats": "📊 <b>Reviews statistics:</b>\n\n"
                "⭐ Average rating: {:.1f}/5\n"
                "📝 Total reviews: {}\n"
                "🎯 Distribution:\n{}",
        "not_admin": "⛔ <b>You don't have administrator rights!</b>"
    }
}

# Эмодзи для рейтинга
rating_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

# ==============================
# 🔘 Кнопка "Отзывы"
# ==============================
@router.callback_query(lambda c: c.data == "reviews")
async def reviews_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")
    
    await call.message.answer(
        "💬 <b>Система отзывов</b>\n\nВыберите действие:",
        reply_markup=reviews_menu(lang, is_admin(user_id))
    )
    await call.answer()

# ==============================
# 🔘 Оставить отзыв
# ==============================
@router.callback_query(lambda c: c.data == "leave_review")
async def leave_review_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")
    
    text = review_texts[lang]["start"]
    await call.message.answer(text, reply_markup=rating_menu(lang))
    await state.set_state(ReviewStates.waiting_for_rating)
    await call.answer()

# ==============================
# 🔘 Выбор рейтинга
# ==============================
@router.callback_query(ReviewStates.waiting_for_rating, lambda c: c.data.startswith("rate_"))
async def process_rating(call: CallbackQuery, state: FSMContext):
    rating = int(call.data.split("_")[1])
    await state.update_data(rating=rating)
    
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")
    
    text = review_texts[lang]["ask_text"]
    await call.message.answer(text)
    await state.set_state(ReviewStates.waiting_for_review)
    await call.answer()

# ==============================
# 🔘 Получение текста отзыва
# ==============================
@router.message(ReviewStates.waiting_for_review)
async def process_review_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    lang = user_languages.get(user_id, "ru")
    review_text = message.text
    rating = user_data['rating']

    # Сохраняем отзыв в базу
    review_id = save_review(user_id, message.from_user.full_name, rating, review_text, lang)

    # ✅ ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ АДМИНАМ
    user_info = {
        'user_id': user_id,
        'full_name': message.from_user.full_name
    }
    await notify_admins_new_review(message.bot, review_id, user_info, rating, review_text)

    # Подтверждение пользователю
    short_review = review_text[:100] + "..." if len(review_text) > 100 else review_text
    user_text = review_texts[lang]["success"].format(rating, short_review)
    await message.answer(user_text, reply_markup=main_menu(lang))
    await state.clear()

# ==============================
# 🔘 Просмотр всех отзывов
# ==============================
@router.callback_query(lambda c: c.data == "view_reviews")
async def view_all_reviews(call: CallbackQuery):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")
    
    reviews = get_reviews()
    
    if not reviews:
        text = review_texts[lang]["no_reviews"]
        await call.message.answer(text)
    else:
        text = review_texts[lang]["all_reviews"]
        for review in reviews[:10]:  # Показываем последние 10 отзывов
            review_id, user_name, rating, review_text, created_at = review
            stars = "⭐" * rating + "☆" * (5 - rating)
            short_text = review_text[:150] + "..." if len(review_text) > 150 else review_text
            
            text += f"👤 <b>{user_name}</b> {stars}\n"
            text += f"📅 {created_at[:10]}\n"
            text += f"💬 {short_text}\n\n"
        
        await call.message.answer(text)
    
    await call.answer()

# ==============================
# 🔘 Статистика отзывов (только для админов)
# ==============================
@router.callback_query(lambda c: c.data == "reviews_stats")
async def reviews_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "ru")
        await call.answer(review_texts[lang]["not_admin"], show_alert=True)
        return
    
    lang = user_languages.get(call.from_user.id, "ru")
    stats = get_review_stats()
    
    # Формируем распределение рейтингов
    distribution = ""
    for i in range(5, 0, -1):
        count = stats['rating_distribution'].get(i, 0)
        percentage = (count / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
        stars = "⭐" * i + "☆" * (5 - i)
        distribution += f"{stars}: {count} ({percentage:.1f}%)\n"
    
    text = review_texts[lang]["stats"].format(
        stats['average_rating'], 
        stats['total_reviews'],
        distribution
    )
    
    await call.message.answer(text)
    await call.answer()

# ==============================
# 🔘 Удаление отзыва (админы)
# ==============================
@router.callback_query(lambda c: c.data.startswith("delete_review_"))
async def delete_review_handler(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "ru")
        await call.answer(review_texts[lang]["not_admin"], show_alert=True)
        return
    
    review_id = int(call.data.split("_")[2])
    delete_review(review_id)
    
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("✅ Отзыв удален")

# Клавиатура для выбора рейтинга
def rating_menu(lang: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for i in range(1, 6):
        buttons.append(InlineKeyboardButton(
            text=f"{rating_emojis[i-1]} {i}",
            callback_data=f"rate_{i}"
        ))
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Добавьте эту функцию в файл, рядом с другими
async def notify_admins_new_review(bot, review_id, user_info, rating, review_text):
    """Уведомление админов о новом отзыве"""
    admin_text = f"⭐ <b>Новый отзыв!</b>\n\n" \
                 f"👤 <b>Пользователь:</b> {user_info['full_name']}\n" \
                 f"🆔 <b>ID:</b> {user_info['user_id']}\n" \
                 f"⭐ <b>Оценка:</b> {rating}/5\n" \
                 f"📋 <b>Отзыв №:</b> {review_id}\n\n" \
                 f"💬 <b>Текст:</b>\n{review_text}"

    # ID группы администраторов (замените на ваш)
    ADMIN_GROUP_ID = -4931417098

    try:
        await bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=admin_text,
            reply_markup=admin_reviews_buttons(review_id) # Кнопки "Удалить", "Скрыть"
        )
    except Exception as e:
        print(f"Ошибка отправки отзыва админам: {e}")
        # Резервная отправка личным сообщением каждому админу
        from data.admins import ADMINS
        for admin_id in ADMINS:
            try:
                await bot.send_message(admin_id, admin_text, reply_markup=admin_reviews_buttons(review_id))
            except:
                pass
            
# ==============================
# ==============================
# 🔘 Удаление и скрытие отзывов
# ==============================
@router.callback_query(lambda c: c.data.startswith(("admin_delete_review_", "admin_hide_review_")))
async def admin_review_actions(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Sizda admin huquqlari yo'q!")
        return

    data = call.data

    if data.startswith("admin_delete_review_"):
        review_id = int(data.split("_")[3])
        delete_review(review_id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer("🗑️ Fikr o'chirildi")

    elif data.startswith("admin_hide_review_"):
        review_id = int(data.split("_")[3])
        hide_review(review_id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer("👁️ Fikr yashirildi")