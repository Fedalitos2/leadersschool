# ============================================
# 🔹 handlers/broadcast.py — система рассылок (ИСПРАВЛЕННАЯ)
# ============================================

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.db import get_all_groups, get_all_users, get_connection
from data.admins import is_admin
from keyboards.admin_buttons import admin_broadcast_buttons, broadcast_confirmation_buttons
from data.languages import user_languages
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from aiogram.filters import Command

router = Router()

# Состояния для создания рассылки
class BroadcastStates(StatesGroup):
    waiting_for_broadcast_text = State()
    waiting_for_broadcast_confirmation = State()

# Тексты для рассылки
broadcast_texts = {
    "ru": {
        "menu": "📢 <b>Система рассылок</b>\n\nВыберите тип рассылки:",
        "input_text": "✍️ <b>Введите текст для рассылки:</b>\n\nПоддерживается HTML разметка",
        "confirm": "✅ <b>Подтвердите рассылку:</b>\n\n{message_text}\n\n📊 <b>Статистика:</b>\n• Группы: {groups_count}\n• Пользователи: {users_count}\n• Всего получателей: {total_recipients}",
        "started": "🚀 <b>Рассылка началась!</b>\n\nОтправляется {total} сообщений...",
        "progress": "📊 <b>Прогресс:</b> {success}/{total} ({percentage}%)",
        "completed": "✅ <b>Рассылка завершена!</b>\n\n📊 <b>Результаты:</b>\n• Успешно: {success}\n• Не удалось: {failed}\n• Всего: {total}",
        "cancelled": "❌ <b>Рассылка отменена</b>",
        "no_recipients": "❌ <b>Нет получателей для рассылки!</b>",
        "not_admin": "⛔ <b>У вас нет прав администратора!</b>"
    },
    "uz": {
        "menu": "📢 <b>Xabar tarqatish tizimi</b>\n\nTarqatish turini tanlang:",
        "input_text": "✍️ <b>Tarqatish uchun matn kiriting:</b>\n\nHTML belgilash qo'llab-quvvatlanadi",
        "confirm": "✅ <b>Tarqatishni tasdiqlang:</b>\n\n{message_text}\n\n📊 <b>Statistika:</b>\n• Guruhlar: {groups_count}\n• Foydalanuvchilar: {users_count}\n• Jami qabul qiluvchilar: {total_recipients}",
        "started": "🚀 <b>Xabar tarqatish boshlandi!</b>\n\n{total} xabar yuborilmoqda...",
        "progress": "📊 <b>Jarayon:</b> {success}/{total} ({percentage}%)",
        "completed": "✅ <b>Xabar tarqatish tugadi!</b>\n\n📊 <b>Natijalar:</b>\n• Muvaffaqiyatli: {success}\n• Muvaffaqiyatsiz: {failed}\n• Jami: {total}",
        "cancelled": "❌ <b>Xabar tarqatish bekor qilindi</b>",
        "no_recipients": "❌ <b>Xabar tarqatish uchun qabul qiluvchilar yo'q!</b>",
        "not_admin": "⛔ <b>Sizda administrator huquqlari yo'q!</b>"
    }
}

# Глобальные переменные для хранения данных рассылки
broadcast_data = {}

# ==============================
# 🔘 Меню рассылки
# ==============================
@router.callback_query(lambda c: c.data == "admin_broadcast")
async def broadcast_menu(call: CallbackQuery):
    """Меню управления рассылками"""
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "uz")
        await call.answer(broadcast_texts[lang]["not_admin"], show_alert=True)
        return
    
    lang = user_languages.get(call.from_user.id, "ru")
    await call.message.edit_text(broadcast_texts[lang]["menu"], reply_markup=admin_broadcast_buttons())
    await call.answer()

# ==============================
# 🔘 Создание рассылки
# ==============================
@router.callback_query(lambda c: c.data in ["broadcast_groups", "broadcast_users", "create_broadcast"])
async def start_broadcast_creation(call: CallbackQuery, state: FSMContext):
    """Начало создания рассылки"""
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "uz")
        await call.answer(broadcast_texts[lang]["not_admin"], show_alert=True)
        return
    
    broadcast_type = "all"  # По умолчанию рассылаем всем
    
    if call.data == "broadcast_groups":
        broadcast_type = "groups"
    elif call.data == "broadcast_users":
        broadcast_type = "users"
    elif call.data == "create_broadcast":
        broadcast_type = "all"
    
    await state.update_data(broadcast_type=broadcast_type)
    
    lang = user_languages.get(call.from_user.id, "ru")
    await call.message.answer(broadcast_texts[lang]["input_text"])
    await state.set_state(BroadcastStates.waiting_for_broadcast_text)
    await call.answer()

# ==============================
# 🔘 Получение текста рассылки
# ==============================
@router.message(BroadcastStates.waiting_for_broadcast_text)
async def process_broadcast_text(message: Message, state: FSMContext):
    """Обработка текста рассылки"""
    user_data = await state.get_data()
    broadcast_type = user_data.get('broadcast_type', 'all')
    
    # Получаем получателей
    recipients = []
    
    if broadcast_type in ["groups", "all"]:
        groups = get_all_groups()
        recipients.extend([(chat_id, 'group') for chat_id in groups])
    
    if broadcast_type in ["users", "all"]:
        users = get_all_users()
        recipients.extend([(user_id, 'user') for user_id in users])
    
    if not recipients:
        lang = user_languages.get(message.from_user.id, "ru")
        await message.answer(broadcast_texts[lang]["no_recipients"])
        await state.clear()
        return
    
    # Сохраняем данные для подтверждения
    broadcast_data[message.from_user.id] = {
        'text': message.text,
        'recipients': recipients,
        'message_id': message.message_id
    }
    
    lang = user_languages.get(message.from_user.id, "ru")
    confirm_text = broadcast_texts[lang]["confirm"].format(
        message_text=message.text[:500] + "..." if len(message.text) > 500 else message.text,
        groups_count=len([r for r in recipients if r[1] == 'group']),
        users_count=len([r for r in recipients if r[1] == 'user']),
        total_recipients=len(recipients)
    )
    
    await message.answer(confirm_text, reply_markup=broadcast_confirmation_buttons())
    await state.set_state(BroadcastStates.waiting_for_broadcast_confirmation)

# ==============================
# 🔘 Подтверждение рассылки
# ==============================
@router.callback_query(BroadcastStates.waiting_for_broadcast_confirmation)
async def confirm_broadcast(call: CallbackQuery, state: FSMContext):
    """Подтверждение и запуск рассылки"""
    if call.data == "cancel_broadcast":
        lang = user_languages.get(call.from_user.id, "ru")
        await call.message.edit_text(broadcast_texts[lang]["cancelled"])
        await state.clear()
        await call.answer()
        return
    
    if call.data == "confirm_broadcast":
        user_id = call.from_user.id
        if user_id not in broadcast_data:
            await call.answer("❌ Данные рассылки не найдены")
            return
        
        data = broadcast_data[user_id]
        recipients = data['recipients']
        text = data['text']
        
        lang = user_languages.get(call.from_user.id, "ru")
        total = len(recipients)
        
        # Отправляем сообщение о начале рассылки
        progress_message = await call.message.answer(
            broadcast_texts[lang]["started"].format(total=total)
        )
        
        # Запускаем рассылку
        success = 0
        failed = 0
        
        for i, (recipient_id, recipient_type) in enumerate(recipients, 1):
            try:
                await call.bot.send_message(
                    chat_id=recipient_id,
                    text=text,
                    parse_mode="HTML"
                )
                success += 1
            except Exception as e:
                failed += 1
                print(f"Ошибка отправки {recipient_type} {recipient_id}: {e}")
            
            # Обновляем прогресс каждые 10 сообщений или в конце
            if i % 10 == 0 or i == total:
                percentage = (i / total) * 100
                try:
                    await progress_message.edit_text(
                        broadcast_texts[lang]["progress"].format(
                            success=success, total=total, percentage=int(percentage)
                        )
                    )
                except:
                    pass
            
            # Небольшая задержка чтобы не превысить лимиты Telegram
            await asyncio.sleep(0.1)
        
        # Завершаем рассылку
        await progress_message.edit_text(
            broadcast_texts[lang]["completed"].format(
                success=success, failed=failed, total=total
            )
        )
        
        # Сохраняем статистику рассылки в базу
        save_broadcast_stats(user_id, text, success, failed, total)
        
        # Очищаем данные
        if user_id in broadcast_data:
            del broadcast_data[user_id]
        
        await state.clear()
        await call.answer()

# ==============================
# 🔘 Статистика рассылок
# ==============================
@router.callback_query(lambda c: c.data == "broadcast_stats")
async def show_broadcast_stats(call: CallbackQuery):
    """Показать статистику рассылок"""
    if not is_admin(call.from_user.id):
        lang = user_languages.get(call.from_user.id, "uz")
        await call.answer(broadcast_texts[lang]["not_admin"], show_alert=True)
        return
    
    stats = get_broadcast_stats()
    
    text = "📊 <b>Статистика рассылок:</b>\n\n"
    text += f"• Всего рассылок: {stats['total_broadcasts']}\n"
    text += f"• Успешных отправок: {stats['total_success']}\n"
    text += f"• Неудачных отправок: {stats['total_failed']}\n"
    text += f"• Общий охват: {stats['total_recipients']}\n\n"
    text += "📈 <b>Последние 5 рассылок:</b>\n\n"
    
    for broadcast in stats['recent_broadcasts']:
        text += f"• {broadcast['date']}: {broadcast['success']}/{broadcast['total']} успешных\n"
    
    await call.message.answer(text)
    await call.answer()

# ==============================
# 🔘 Функции для работы с базой данных
# ==============================
def save_broadcast_stats(admin_id: int, text: str, success: int, failed: int, total: int):
    """Сохранить статистику рассылки в базу"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        message_text TEXT NOT NULL,
        success_count INTEGER NOT NULL,
        failed_count INTEGER NOT NULL,
        total_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    INSERT INTO broadcasts (admin_id, message_text, success_count, failed_count, total_count)
    VALUES (?, ?, ?, ?, ?)
    ''', (admin_id, text[:1000], success, failed, total))
    
    conn.commit()
    conn.close()

def get_broadcast_stats():
    """Получить статистику рассылок"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу если не существует
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        message_text TEXT NOT NULL,
        success_count INTEGER NOT NULL,
        failed_count INTEGER NOT NULL,
        total_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    stats = {}
    
    # Общая статистика
    cursor.execute('SELECT COUNT(*) FROM broadcasts')
    stats['total_broadcasts'] = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(success_count), SUM(failed_count), SUM(total_count) FROM broadcasts')
    result = cursor.fetchone()
    stats['total_success'] = result[0] or 0
    stats['total_failed'] = result[1] or 0
    stats['total_recipients'] = result[2] or 0
    
    # Последние 5 рассылок
    cursor.execute('''
    SELECT DATE(created_at), success_count, total_count 
    FROM broadcasts 
    ORDER BY created_at DESC 
    LIMIT 5
    ''')
    
    recent = []
    for date, success, total in cursor.fetchall():
        recent.append({
            'date': date,
            'success': success,
            'total': total
        })
    
    stats['recent_broadcasts'] = recent
    
    conn.close()
    return stats

# ==============================
# 🔘 Команда для прямой рассылки
# ==============================
@router.message(Command("broadcast"))
async def direct_broadcast_command(message: Message, state: FSMContext):
    """Прямая команда для рассылки"""
    if not is_admin(message.from_user.id):
        lang = user_languages.get(message.from_user.id, "uz")
        await message.answer(broadcast_texts[lang]["not_admin"])
        return
    
    # Проверяем есть ли текст после команды
    if not message.text or len(message.text.split()) < 2:
        await message.answer("❌ <b>Использование:</b> /broadcast [текст сообщения]")
        return
    
    # Извлекаем текст сообщения (убираем команду)
    broadcast_text = message.text.split(' ', 1)[1]
    
    # Получаем всех получателей
    recipients = []
    groups = get_all_groups()
    users = get_all_users()
    
    recipients.extend([(chat_id, 'group') for chat_id in groups])
    recipients.extend([(user_id, 'user') for user_id in users])
    
    if not recipients:
        await message.answer("❌ Нет получателей для рассылки!")
        return
    
    total = len(recipients)
    success = 0
    failed = 0
    
    # Отправляем сообщение о начале рассылки
    progress_message = await message.answer(f"🚀 <b>Начинаю рассылку...</b>\n\nПолучателей: {total}")
    
    # Запускаем рассылку
    for i, (recipient_id, recipient_type) in enumerate(recipients, 1):
        try:
            await message.bot.send_message(
                chat_id=recipient_id,
                text=broadcast_text,
                parse_mode="HTML"
            )
            success += 1
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки {recipient_type} {recipient_id}: {e}")
        
        # Обновляем прогресс каждые 10 сообщений
        if i % 10 == 0 or i == total:
            percentage = (i / total) * 100
            try:
                await progress_message.edit_text(
                    f"📊 <b>Прогресс рассылки:</b>\n\n"
                    f"• Отправлено: {i}/{total}\n"
                    f"• Успешно: {success}\n"
                    f"• Ошибок: {failed}\n"
                    f"• Завершено: {int(percentage)}%"
                )
            except:
                pass
        
        # Небольшая задержка
        await asyncio.sleep(0.1)
    
    # Завершаем рассылку
    await progress_message.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📊 <b>Результаты:</b>\n"
        f"• Успешно: {success}\n"
        f"• Ошибок: {failed}\n"
        f"• Всего: {total}"
    )
    
    # Сохраняем статистику
    save_broadcast_stats(message.from_user.id, broadcast_text, success, failed, total)