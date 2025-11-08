# ============================================
# 🔹 handlers/admin.py — administrator harakatlari
# ============================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from data.db import update_application_status, update_question_status, get_statistics, get_user_count
from data.languages import user_languages
from data.admins import is_admin, ADMINS
from keyboards.admin_buttons import admin_panel_buttons
from data.db import get_pending_applications_count, get_pending_questions_count, get_recent_applications, get_recent_questions
from keyboards.admin_buttons import admin_panel_buttons

router = Router()

# Состояние для ответа на вопрос
class AnswerState(StatesGroup):
    waiting_for_answer = State()

# Foydalanuvchilarga javob matnlari
response_texts = {
    "ru": {
        "approved": "✅ <b>Ваша заявка одобрена!</b>\n\nАдминистратор свяжется с вами для уточнения деталей.",
        "rejected": "❌ <b>Ваша заявка отклонена.</b>\n\nДля уточнения информации обратитесь к администратору.",
        "answered": "💬 <b>Ответ на ваш вопрос:</b>\n\n{}",
        "not_admin": "⛔ <b>У вас нет прав администратора!</b>"
    },
    "uz": {
        "approved": "✅ <b>Arizangiz qabul qilindi!</b>\n\nAdministrator tafsilotlar uchun siz bilan bog'lanadi.",
        "rejected": "❌ <b>Arizangiz rad etildi.</b>\n\nMa'lumot uchun administratorga murojaat qiling.",
        "answered": "💬 <b>Savolingizga javob:</b>\n\n{}",
        "not_admin": "⛔ <b>Sizda administrator huquqlari yo'q!</b>"
    },
    "en": {
        "approved": "✅ <b>Your application has been approved!</b>\n\nAdministrator will contact you for details.",
        "rejected": "❌ <b>Your application has been rejected.</b>\n\nContact administrator for information.",
        "answered": "💬 <b>Answer to your question:</b>\n\n{}",
        "not_admin": "⛔ <b>You don't have administrator rights!</b>"
    }
}

# ==============================
# 🔘 Administrator harakatlarini qayta ishlash
# ==============================
@router.callback_query(lambda c: c.data.startswith(("approve_", "reject_", "contact_", "delete_", "answer_question_", "question_done_", "delete_question_")))
async def admin_action(call: CallbackQuery, state: FSMContext):
    # Administratorlik huquqini tekshirish
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "uz")
        await call.answer(response_texts[lang]["not_admin"], show_alert=True)
        return
    
    data = call.data
    admin_id = call.from_user.id
    
    if data.startswith("approve_"):
        # Qabul qilish
        parts = data.split("_")
        target_user_id = int(parts[1])
        application_id = int(parts[2])
        
        # Foydalanuvchi tilini olish
        user_lang = user_languages.get(target_user_id, "uz")
        
        # Ariza statusini yangilash
        update_application_status(application_id, "qabul qilindi", admin_id, "Ariza qabul qilindi")
        
        # Foydalanuvchiga xabar (o'z tilida)
        user_text = response_texts[user_lang]["approved"]
        
        try:
            await call.bot.send_message(chat_id=target_user_id, text=user_text)
        except:
            pass
            
        await call.answer("✅ Ariza qabul qilindi")
        await call.message.edit_reply_markup(reply_markup=None)
        
    elif data.startswith("reject_"):
        # Rad etish
        parts = data.split("_")
        target_user_id = int(parts[1])
        application_id = int(parts[2])
        
        # Foydalanuvchi tilini olish
        user_lang = user_languages.get(target_user_id, "uz")
        
        # Ariza statusini yangilash
        update_application_status(application_id, "rad etildi", admin_id, "Ariza rad etildi")
        
        # Foydalanuvchiga xabar (o'z tilida)
        user_text = response_texts[user_lang]["rejected"]
        
        try:
            await call.bot.send_message(chat_id=target_user_id, text=user_text)
        except:
            pass
            
        await call.answer("❌ Ariza rad etildi")
        await call.message.edit_reply_markup(reply_markup=None)
        
    elif data.startswith("answer_question_"):
        # Ответить на вопрос
        parts = data.split("_")
        target_user_id = int(parts[2])
        question_id = int(parts[3])
        
        # Сохраняем данные для ответа
        await state.update_data(target_user_id=target_user_id, question_id=question_id)
        await call.message.answer("💬 <b>Введите ответ для пользователя:</b>")
        await state.set_state(AnswerState.waiting_for_answer)
        await call.answer()
        
    elif data.startswith("question_done_"):
        # Отметить как отвеченное
        question_id = int(data.split("_")[2])
        update_question_status(question_id, "answered", call.from_user.id)
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer("✅ Вопрос отмечен как отвеченный")
        
    elif data.startswith("contact_"):
        # Bog'lanish
        target_user_id = int(data.split("_")[1])
        await call.answer(f"Foydalanuvchi ID: {target_user_id}")
        
    elif data.startswith("delete_"):
        # O'chirish
        application_id = int(data.split("_")[1])
        await call.message.delete()
        await call.answer("🗑️ Ariza o'chirildi")
        
    elif data.startswith("delete_question_"):
        # Удалить вопрос
        question_id = int(data.split("_")[2])
        await call.message.delete()
        await call.answer("🗑️ Вопрос удален")

# ==============================
# 🔘 Обработка ответа на вопрос
# ==============================
@router.message(AnswerState.waiting_for_answer)
async def process_admin_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    
    if 'target_user_id' in user_data and 'question_id' in user_data:
        target_user_id = user_data['target_user_id']
        question_id = user_data['question_id']
        answer_text = message.text
        
        # Получаем язык пользователя
        user_lang = user_languages.get(target_user_id, "uz")
        
        # Отправляем ответ пользователю
        try:
            response_text = response_texts[user_lang]["answered"].format(answer_text)
            await message.bot.send_message(chat_id=target_user_id, text=response_text)
            
            # Обновляем статус вопроса
            update_question_status(question_id, "answered", message.from_user.id, answer_text)
            
            await message.answer("✅ Ответ отправлен пользователю!")
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки: {e}")
        
        await state.clear()

# Тексты для статистики
stats_texts = {
    "ru": {
        "title": "📊 <b>СТАТИСТИКА БОТА</b>\n\n",
        "users": "👥 <b>Пользователи:</b>\n"
                "• Всего пользователей: {total_users}\n"
                "• Подали заявки: {applications_users}\n"
                "• Задали вопросы: {questions_users}\n\n",
        "applications": "📝 <b>Заявки:</b>\n"
                       "• Всего заявок: {total_applications}\n"
                       "• Ожидают: {pending_applications}\n"
                       "• Одобрены: {approved_applications}\n"
                       "• Отклонены: {rejected_applications}\n\n",
        "questions": "❓ <b>Вопросы:</b>\n"
                    "• Всего вопросов: {total_questions}\n"
                    "• Ожидают ответа: {pending_questions}\n"
                    "• Ответили: {answered_questions}\n\n",
        "recent": "📈 <b>Активность за 7 дней:</b>\n"
                 "• Заявок: {app_last_7_days}\n"
                 "• Вопросов: {quest_last_7_days}\n\n",
        "popular": "🎯 <b>Популярные курсы:</b>\n{popular_courses}",
        "not_admin": "⛔ <b>У вас нет прав администратора!</b>"
    },
    "uz": {
        "title": "📊 <b>BOT STATISTIKASI</b>\n\n",
        "users": "👥 <b>Foydalanuvchilar:</b>\n"
                "• Jami foydalanuvchilar: {total_users}\n"
                "• Ariza yuborganlar: {applications_users}\n"
                "• Savol berganlar: {questions_users}\n\n",
        "applications": "📝 <b>Arizalar:</b>\n"
                       "• Jami arizalar: {total_applications}\n"
                       "• Kutayotgan: {pending_applications}\n"
                       "• Qabul qilingan: {approved_applications}\n"
                       "• Rad etilgan: {rejected_applications}\n\n",
        "questions": "❓ <b>Savollar:</b>\n"
                    "• Jami savollar: {total_questions}\n"
                    "• Javob kutayotgan: {pending_questions}\n"
                    "• Javob berilgan: {answered_questions}\n\n",
        "recent": "📈 <b>7 kunlik faollik:</b>\n"
                 "• Arizalar: {app_last_7_days}\n"
                 "• Savollar: {quest_last_7_days}\n\n",
        "popular": "🎯 <b>Mashhur kurslar:</b>\n{popular_courses}",
        "not_admin": "⛔ <b>Sizda administrator huquqlari yo'q!</b>"
    },
    "en": {
        "title": "📊 <b>BOT STATISTICS</b>\n\n",
        "users": "👥 <b>Users:</b>\n"
                "• Total users: {total_users}\n"
                "• Applied: {applications_users}\n"
                "• Asked questions: {questions_users}\n\n",
        "applications": "📝 <b>Applications:</b>\n"
                       "• Total applications: {total_applications}\n"
                       "• Pending: {pending_applications}\n"
                       "• Approved: {approved_applications}\n"
                       "• Rejected: {rejected_applications}\n\n",
        "questions": "❓ <b>Questions:</b>\n"
                    "• Total questions: {total_questions}\n"
                    "• Waiting: {pending_questions}\n"
                    "• Answered: {answered_questions}\n\n",
        "recent": "📈 <b>Activity last 7 days:</b>\n"
                 "• Applications: {app_last_7_days}\n"
                 "• Questions: {quest_last_7_days}\n\n",
        "popular": "🎯 <b>Popular courses:</b>\n{popular_courses}",
        "not_admin": "⛔ <b>You don't have administrator rights!</b>"
    }
}

# ==============================
# 🔘 Команда /stats
# ==============================
@router.message(Command("stats"))
async def stats_command(message: Message):
    """Показать статистику бота"""
    # Проверяем права администратора
    if not is_admin(message.from_user.id):
        lang = user_languages.get(message.from_user.id, "uz")
        await message.answer(stats_texts[lang]["not_admin"])
        return
    
    # Получаем статистику
    stats = get_statistics()
    users_stats = get_user_count()
    lang = user_languages.get(message.from_user.id, "ru")
    
    # Форматируем популярные курсы
    popular_courses = ""
    for course, count in stats['popular_courses']:
        popular_courses += f"• {course}: {count}\n"
    
    # Считаем заявки и вопросы за 7 дней
    app_last_7_days = sum(count for _, count in stats['applications_last_7_days'])
    quest_last_7_days = sum(count for _, count in stats['questions_last_7_days'])
    
    # Формируем текст статистики
    text = (
        stats_texts[lang]["title"] +
        stats_texts[lang]["users"].format(
            total_users=users_stats['total_users'],
            applications_users=users_stats['applications_users'],
            questions_users=users_stats['questions_users']
        ) +
        stats_texts[lang]["applications"].format(
            total_applications=stats['total_applications'],
            pending_applications=stats['pending_applications'],
            approved_applications=stats['approved_applications'],
            rejected_applications=stats['rejected_applications']
        ) +
        stats_texts[lang]["questions"].format(
            total_questions=stats['total_questions'],
            pending_questions=stats['pending_questions'],
            answered_questions=stats['answered_questions']
        ) +
        stats_texts[lang]["recent"].format(
            app_last_7_days=app_last_7_days,
            quest_last_7_days=quest_last_7_days
        ) +
        stats_texts[lang]["popular"].format(popular_courses=popular_courses)
    )
    
    await message.answer(text)

# ==============================
# 🔘 Команда /panel
# ==============================
@router.message(Command("panel"))
async def admin_panel_command(message: Message):
    """Админ-панель"""
    if not is_admin(message.from_user.id):
        lang = user_languages.get(message.from_user.id, "uz")
        await message.answer(response_texts[lang]["not_admin"])
        return
    
    pending_apps = get_pending_applications_count()
    pending_questions = get_pending_questions_count()
    
    text = f"👑 <b>Admin Panel</b>\n\n" \
           f"📊 <b>Statistika:</b>\n" \
           f"• 📝 Kutayotgan arizalar: {pending_apps}\n" \
           f"• ❓ Kutayotgan savollar: {pending_questions}\n\n" \
           f"🛠 <b>Boshqaruv:</b>\n" \
           f"Quyidagi tugmalar orqali boshqaring"
    
    await message.answer(text, reply_markup=admin_panel_buttons())

# ==============================
# 🔘 Обработка кнопок админ-панели
# ==============================
@router.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_panel_actions(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔ Sizda admin huquqlari yo'q!")
        return
    
    data = call.data
    
    if data == "admin_stats":
        # Перенаправляем на статистику
        await stats_command(call.message)
        await call.answer()
        
    elif data == "admin_pending_apps":
        # Показываем ожидающие заявки
        applications = get_recent_applications(10)
        
        if not applications:
            text = "📝 <b>Kutayotgan arizalar yo'q</b>\n\nHozircha yangi ariza kelmagan."
            await call.message.answer(text)
        else:
            text = "📝 <b>So'ngi 10 ta ariza:</b>\n\n"
            for app in applications:
                app_id, user_id, full_name, course, created_at = app
                text += f"🔹 <b>#{app_id}</b> - {full_name}\n" \
                       f"   📚 {course}\n" \
                       f"   ⏰ {created_at[:16]}\n" \
                       f"   👤 ID: {user_id}\n\n"
            
            await call.message.answer(text)
        await call.answer()
        
    elif data == "admin_pending_questions":
        # Показываем ожидающие вопросы
        questions = get_recent_questions(10)
        
        if not questions:
            text = "❓ <b>Kutayotgan savollar yo'q</b>\n\nHozircha yangi savol kelmagan."
            await call.message.answer(text)
        else:
            text = "❓ <b>So'ngi 10 ta savol:</b>\n\n"
            for quest in questions:
                quest_id, user_id, question_text, created_at = quest
                # Обрезаем длинный текст
                short_text = question_text[:100] + "..." if len(question_text) > 100 else question_text
                text += f"🔹 <b>#{quest_id}</b>\n" \
                       f"   👤 ID: {user_id}\n" \
                       f"   💬 {short_text}\n" \
                       f"   ⏰ {created_at[:16]}\n\n"
            
            await call.message.answer(text)
        await call.answer()
        
    elif data == "admin_users":
        # Статистика по пользователям
        users_stats = get_user_count()
        text = f"👥 <b>Foydalanuvchi statistikasi:</b>\n\n" \
               f"• Jami foydalanuvchilar: {users_stats['total_users']}\n" \
               f"• Ariza yuborganlar: {users_stats['applications_users']}\n" \
               f"• Savol berganlar: {users_stats['questions_users']}\n" \
               f"• Faqat ko'rib chiqqanlar: {users_stats['total_users'] - users_stats['applications_users'] - users_stats['questions_users']}"
        
        await call.message.answer(text)
        await call.answer()
        
    elif data == "admin_reviews":
        # Fikr-mulohazalar statistikasi
        from data.db import get_review_stats
        stats = get_review_stats()
        
        lang = user_languages.get(call.from_user.id, "uz")
        text = f"⭐ <b>Fikr-mulohazalar statistikasi</b>\n\n" \
               f"📊 Jami fikrlar: {stats['total_reviews']}\n" \
               f"🌟 O'rtacha reyting: {stats['average_rating']:.1f}/5\n\n" \
               f"📈 Taqsimot:\n"
        
        for rating in range(5, 0, -1):
            count = stats['rating_distribution'].get(rating, 0)
            percentage = (count / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
            stars = "⭐" * rating + "☆" * (5 - rating)
            text += f"{stars}: {count} ({percentage:.1f}%)\n"
        
        await call.message.answer(text)
        
    elif data == "admin_reviews_list":
        # Fikr-mulohazalar ro'yxati
        from data.db import get_reviews
        reviews = get_reviews(limit=15)
        
        if not reviews:
            text = "📝 <b>Hali fikr-mulohazalar yo'q</b>"
            await call.message.answer(text)
        else:
            text = "📋 <b>Oxirgi 15 ta fikr:</b>\n\n"
            for review in reviews:
                review_id, user_name, rating, review_text, created_at = review
                stars = "⭐" * rating + "☆" * (5 - rating)
                short_text = review_text[:80] + "..." if len(review_text) > 80 else review_text
                
                text += f"🔹 <b>#{review_id}</b> {stars}\n" \
                       f"👤 {user_name}\n" \
                       f"💬 {short_text}\n" \
                       f"📅 {created_at[:10]}\n\n"
            
            await call.message.answer(text)
    
    elif data == "admin_notifications":
        # Bildirishnomalarni boshqarish
        text = "🔔 <b>Bildirishnomalarni boshqarish</b>\n\n" \
               "Yangi ariza va savollar haqida bildirishnoma olishni sozlashingiz mumkin."
        await call.message.answer(text)
        
    elif data == "admin_settings":
        # Bot sozlamalari
        text = "⚙️ <b>Bot sozlamalari</b>\n\n" \
               "Bu yerda botning turli parametrlarini sozlashingiz mumkin."
        await call.message.answer(text)
        
    elif data == "admin_refresh":
        # Обновить панель
        await call.message.delete()
        await admin_panel_command(call.message)
        await call.answer("🔄 Panel yangilandi")
        
    elif data == "admin_close":
        # Закрыть панель
        await call.message.delete()
        await call.answer("✅ Panel yopildi")
# 🔘 Обработка кнопки рассылки
# ==============================
    elif data == "admin_broadcast":
    # Перенаправляем на модуль рассылки
      from handlers.broadcast import broadcast_menu
    await broadcast_menu(call)

    await call.answer()

# ==============================
# 🔘 Уведомления администраторов
# ==============================
async def notify_admins_new_application(bot, application_id, user_info):
    """Уведомление админов о новой заявке"""
    for admin_id in ADMINS:
        try:
            text = f"🔔 <b>Yangi ariza!</b>\n\n" \
                   f"📋 Ariza №: {application_id}\n" \
                   f"👤 Foydalanuvchi: {user_info['full_name']}\n" \
                   f"📚 Kurs: {user_info['course']}\n" \
                   f"📞 Tel: {user_info['phone']}"
            
            await bot.send_message(admin_id, text)
        except:
            pass

async def notify_admins_new_question(bot, question_id, user_info):
    """Уведомление админов о новом вопросе"""
    for admin_id in ADMINS:
        try:
            text = f"🔔 <b>Yangi savol!</b>\n\n" \
                   f"📋 Savol №: {question_id}\n" \
                   f"👤 Foydalanuvchi: {user_info['full_name']}\n" \
                   f"💬 Savol: {user_info['question_text'][:100]}..."
            
            await bot.send_message(admin_id, text)
        except:
            pass
        
