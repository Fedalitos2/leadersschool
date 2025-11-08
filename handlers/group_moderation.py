# ============================================
# 🔹 handlers/group_moderation.py — группа модерация функциялари
# ============================================

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import sqlite3
import re
from data.db import get_all_groups
from data.admins import is_admin as is_global_admin

router = Router()

# ==============================
# 🔘 Функция для проверки, является ли бот админом в группе
# ==============================
async def is_bot_admin(bot, chat_id: int) -> bool:
    """Проверяет, является ли бот администратором в группе"""
    try:
        member = await bot.get_chat_member(chat_id, bot.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False
      

# База данных для заметок и мутов
NOTES_DB = "group_data.db"

def init_group_db():
    """Группа маълумотлар базасини ишга тушириш"""
    conn = sqlite3.connect(NOTES_DB)
    cursor = conn.cursor()
    
    # Заметкалар учун таблица
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        trigger TEXT NOT NULL,
        content TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Мутлар учун таблица
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mutes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        muted_until TIMESTAMP NOT NULL,
        muted_by INTEGER NOT NULL,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Админлар учун таблица
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        added_by INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Группа маълумотлар базаси ишга тушди")

def get_group_connection():
    """Группа базаси билан боғланиш"""
    return sqlite3.connect(NOTES_DB)

# Тексты на узбекском языке
TEXTS = {
    "ban_success": "✅ <b>{user}</b> гуруҳдан ҳақиқий ҳайдаб юборилди!",
    "ban_error": "❌ Фойдаланувчини ҳайдаб бўлмади. Мен ундан юқорироқ ҳуқуқға эгаман.",
    "kick_success": "✅ <b>{user}</b> гуруҳдан чиқариб юборилди!",
    "kick_error": "❌ Фойдаланувчини чиқариб бўлмади.",
    "mute_success": "🔇 <b>{user}</b> {time} муддатга овозсизланди!",
    "mute_error": "❌ Фойдаланувчини овозсизлантириб бўлмади.",
    "unmute_success": "🔊 <b>{user}</b> овози қайтарилди!",
    "unmute_error": "❌ Фойдаланувчини овозини қайтариб бўлмади.",
    "note_added": "📝 <b>Янги эслатма қўшилди:</b>\nТриггер: <code>{trigger}</code>\nМазмуни: {content}",
    "note_removed": "🗑️ <b>Эслатма ўчирилди:</b> #{note_id}",
    "note_not_found": "❌ Бундай ID га эга эслатма топилмади.",
    "note_triggered": "📌 <b>Эслатма:</b>\n{content}",
    "admin_added": "👑 <b>{user}</b> гуруҳда администратор қилиб тайинланди!",
    "admin_removed": "👑 <b>{user}</b> гуруҳдан администраторлик ҳуқуқи олиб ташланди!",
    "admin_list": "👑 <b>Гуруҳ администраторлари:</b>\n\n{admins}",
    "no_admins": "❌ Гуруҳда ҳеч қандай администратор йўқ.",
    "message_deleted": "🗑️ <b>Хабар ўчирилди!</b>",
    "no_permission": "⛔ <b>Сизда бу ҳаракатни бажариш учун ҳуқуқ йўқ!</b>",
    "user_not_found": "❌ Фойдаланувчи топилмади.",
    "syntax_error": "❌ <b>Нотўғри синтаксис!</b>\nТўғри фойдаланиш: <code>{syntax}</code>",
    "broadcast_success": "📢 <b>Хабар {count} та гуруҳга юборилди!</b>",
    "broadcast_error": "❌ Хабарни юборишда хатолик юз берди."
}

# Время мута по умолчанию
MUTE_TIMES = {
    "5m": timedelta(minutes=5),
    "30m": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "6h": timedelta(hours=6),
    "1d": timedelta(days=1),
    "7d": timedelta(days=7)
}

# ==============================
# 🔘 Админлик ҳуқуқини текшириш
# ==============================
# Исправьте функцию проверки прав
async def is_global_admin(user_id: int) -> bool:
    """Проверка глобальных прав администратора"""
    return is_global_admin(user_id)

# ==============================
# ==============================
# 🔘 Бан с временем
# ==============================
@router.message(Command("ban"))
async def ban_user(message: Message, command: CommandObject):
    """Фойдаланувчини гуруҳдан бан қилиш"""
    if not await is_bot_admin(message.bot, message.chat.id):
        return
    
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/ban [кун] [сабаб] - хабарга жавобан"))
        return
    
    target_user = message.reply_to_message.from_user
    args = command.args.split() if command.args else []
    
    if not args:
        ban_days = 0  # Навсегда
        reason = "Сабаб кўрсатилмаган"
    else:
        try:
            ban_days = int(args[0])
            reason = ' '.join(args[1:]) if len(args) > 1 else "Сабаб кўрсатилмаган"
        except ValueError:
            ban_days = 0
            reason = ' '.join(args) if args else "Сабаб кўрсатилмаган"
    
    try:
        if ban_days > 0:
            # Временный бан
            until_date = datetime.now() + timedelta(days=ban_days)
            await message.bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=target_user.id,
                until_date=until_date
            )
            await message.reply(f"✅ <b>{target_user.full_name}</b> {ban_days} кунга бан қилинди!\n🗒 Сабаб: {reason}")
        else:
            # Перманентный бан
            await message.bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=target_user.id
            )
            await message.reply(f"✅ <b>{target_user.full_name}</b> муддатсиз бан қилинди!\n🗒 Сабаб: {reason}")
    except Exception as e:
        await message.reply(TEXTS["ban_error"])

# ==============================
# 🔘 Чиқариб юбориш
# ==============================
@router.message(Command("kick"))
async def kick_user(message: Message):
    """Фойдаланувчини гуруҳдан чиқариш"""
    if not await is_bot_admin(message.bot, message.chat.id):
        return
    
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/kick [сабаб] - хабарга жавобан"))
        return
    
    target_user = message.reply_to_message.from_user
    reason = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else "Сабаб кўрсатилмаган"
    
    try:
        await message.bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=target_user.id,
            until_date=datetime.now() + timedelta(seconds=30)
        )
        await message.reply(TEXTS["kick_success"].format(user=target_user.full_name))
    except Exception as e:
        await message.reply(TEXTS["kick_error"])

# ==============================
# Клавиатура для выбора времени мута
def mute_time_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5 дақиқа", callback_data="mute_5m"),
            InlineKeyboardButton(text="30 дақиқа", callback_data="mute_30m")
        ],
        [
            InlineKeyboardButton(text="1 соат", callback_data="mute_1h"),
            InlineKeyboardButton(text="6 соат", callback_data="mute_6h")
        ],
        [
            InlineKeyboardButton(text="1 кун", callback_data="mute_1d"),
            InlineKeyboardButton(text="7 кун", callback_data="mute_7d")
        ],
        [
            InlineKeyboardButton(text="❌ Бекор қилиш", callback_data="mute_cancel")
        ]
    ])

# ==============================
# 🔘 Улучшенный мут с выбором времени
# ==============================
@router.message(Command("mute"))
async def mute_user_command(message: Message):
    """Фойдаланувчини овозсизлантириш"""
    if not await is_bot_admin(message.bot, message.chat.id):
        return
    
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/mute - хабарга жавобан"))
        return
    
    # Сохраняем информацию о пользователе
    target_user = message.reply_to_message.from_user
    reason = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else "Сабаб кўрсатилмаган"
    
    # Сохраняем в состоянии
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.base import StorageKey
    
    # Создаем FSMContext для этого чата и пользователя
    storage_key = StorageKey(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        bot_id=message.bot.id
    )
    
    # Используем глобальный диспетчер для доступа к storage
    from bot import dp
    state = FSMContext(storage=dp.storage, key=storage_key)
    
    await state.update_data(
        target_user_id=target_user.id,
        target_user_name=target_user.full_name,
        reason=reason
    )
    
    # Показываем клавиатуру выбора времени
    await message.reply(
        f"⏰ <b>{target_user.full_name}</b> учун муддатни танланг:",
        reply_markup=mute_time_keyboard()
    )

# Обработка выбора времени мута
@router.callback_query(lambda c: c.data.startswith("mute_"))
async def process_mute_time(call: CallbackQuery, state: FSMContext):
    if call.data == "mute_cancel":
        await call.message.delete()
        await call.answer("❌ Мут бекор қилинди")
        await state.clear()
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    target_user_id = data['target_user_id']
    target_user_name = data['target_user_name']
    reason = data['reason']
    
    # Определяем время мута
    time_key = call.data.split("_")[1]
    mute_times = {
        "5m": ("5 дақиқа", timedelta(minutes=5)),
        "30m": ("30 дақиқа", timedelta(minutes=30)),
        "1h": ("1 соат", timedelta(hours=1)),
        "6h": ("6 соат", timedelta(hours=6)),
        "1d": ("1 кун", timedelta(days=1)),
        "7d": ("7 кун", timedelta(days=7))
    }
    
    time_str, mute_time = mute_times.get(time_key, ("1 соат", timedelta(hours=1)))
    muted_until = datetime.now() + mute_time
    
    try:
        await call.bot.restrict_chat_member(
            chat_id=call.message.chat.id,
            user_id=target_user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            ),
            until_date=muted_until
        )
        
        # Мутни базага сақлаш
        conn = get_group_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO mutes (user_id, group_id, muted_until, muted_by, reason)
        VALUES (?, ?, ?, ?, ?)
        ''', (target_user_id, call.message.chat.id, muted_until, call.from_user.id, reason))
        conn.commit()
        conn.close()
        
        await call.message.edit_text(
            f"🔇 <b>{target_user_name}</b> {time_str} муддатга овозсизланди!\n🗒 Сабаб: {reason}"
        )
        
    except Exception as e:
        await call.message.edit_text(TEXTS["mute_error"])
    
    await state.clear()

# ==============================
# 🔘 Овозини қайтариш
# ==============================
@router.message(Command("unmute"))
async def unmute_user(message: Message):
    """Фойдаланувчининг овозини қайтариш"""
    if not await is_bot_admin(message.bot, message.chat.id):
        return
    
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/unmute - хабарга жавобан"))
        return
    
    target_user = message.reply_to_message.from_user
    
    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        
        # Мутни базадан ўчириш
        conn = get_group_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM mutes 
        WHERE user_id = ? AND group_id = ?
        ''', (target_user.id, message.chat.id))
        conn.commit()
        conn.close()
        
        await message.reply(TEXTS["unmute_success"].format(user=target_user.full_name))
    except Exception as e:
        await message.reply(TEXTS["unmute_error"])

# ==============================
# 🔘 Хабарни ўчириш
# ==============================
@router.message(Command("del"))
async def delete_message(message: Message):
    """Хабарни ўчириш"""
    if not await is_bot_admin(message.bot, message.chat.id):
        return
    
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/del - ўчириш учун хабарга жавоб беринг"))
        return
    
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id
        )
        await message.delete()
    except:
        pass

# ==============================
# 🔘 Эслатма қўшиш
# ==============================
@router.message(Command("note"))
async def add_note(message: Message, command: CommandObject):
    """Янги эслатма қўшиш"""
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not command.args:
        await message.reply(TEXTS["syntax_error"].format(syntax="/note [триггер] [матн]"))
        return
    
    args = command.args.split(' ', 1)
    if len(args) < 2:
        await message.reply(TEXTS["syntax_error"].format(syntax="/note [триггер] [матн]"))
        return
    
    trigger = args[0].lower()
    content = args[1]
    
    conn = get_group_connection()
    cursor = conn.cursor()
    
    # Триггер мавжудлигини текшириш
    cursor.execute('''
    SELECT id FROM notes 
    WHERE group_id = ? AND trigger = ?
    ''', (message.chat.id, trigger))
    
    existing_note = cursor.fetchone()
    
    if existing_note:
        # Янгиланган эслатма
        cursor.execute('''
        UPDATE notes SET content = ?, created_by = ?
        WHERE id = ?
        ''', (content, message.from_user.id, existing_note[0]))
    else:
        # Янги эслатма
        cursor.execute('''
        INSERT INTO notes (group_id, trigger, content, created_by)
        VALUES (?, ?, ?, ?)
        ''', (message.chat.id, trigger, content, message.from_user.id))
    
    conn.commit()
    conn.close()
    
    await message.reply(TEXTS["note_added"].format(trigger=trigger, content=content))

# ==============================
# 🔘 Эслатмани ўчириш
# ==============================
@router.message(Command("delnote"))
async def delete_note(message: Message, command: CommandObject):
    """Эслатмани ўчириш"""
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not command.args:
        await message.reply(TEXTS["syntax_error"].format(syntax="/delnote [ID]"))
        return
    
    try:
        note_id = int(command.args)
    except ValueError:
        await message.reply(TEXTS["syntax_error"].format(syntax="/delnote [ID]"))
        return
    
    conn = get_group_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM notes 
    WHERE id = ? AND group_id = ?
    ''', (note_id, message.chat.id))
    
    if cursor.rowcount > 0:
        conn.commit()
        await message.reply(TEXTS["note_removed"].format(note_id=note_id))
    else:
        await message.reply(TEXTS["note_not_found"])
    
    conn.close()

# ==============================
# 🔘 Эслатмаларни кўрсатиш
# ==============================
@router.message(Command("notes"))
async def show_notes(message: Message):
    """Барча эслатмаларни кўрсатиш"""
    conn = get_group_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, trigger, content FROM notes 
    WHERE group_id = ? 
    ORDER BY id
    ''', (message.chat.id,))
    
    notes = cursor.fetchall()
    conn.close()
    
    if not notes:
        await message.reply("📝 <b>Ҳеч қандай эслатма топилмади.</b>")
        return
    
    text = "📋 <b>Гуруҳ эслатмалари:</b>\n\n"
    for note_id, trigger, content in notes:
        short_content = content[:50] + "..." if len(content) > 50 else content
        text += f"🔹 <b>#{note_id}</b> - <code>{trigger}</code>\n{short_content}\n\n"
    
    await message.reply(text)

# ==============================
# 🔘 Эслатма триггерларини қайта ишлаш
# ==============================
@router.message(F.text)
async def handle_note_triggers(message: Message):
    """Эслатма триггерларини аниклаш"""
    if not message.text or message.text.startswith('/'):
        return
    
    text = message.text.lower().strip()
    
    conn = get_group_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT content FROM notes 
    WHERE group_id = ? AND trigger = ?
    ''', (message.chat.id, text))
    
    note = cursor.fetchone()
    conn.close()
    
    if note:
        await message.reply(TEXTS["note_triggered"].format(content=note[0]))

# ==============================
# 🔘 Администратор қўшиш
# ==============================
@router.message(Command("addadmin"))
async def add_admin(message: Message):
    """Янги администратор қўшиш"""
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    target_user = message.reply_to_message.from_user
    
    conn = get_group_connection()
    cursor = conn.cursor()
    
    # Администратор мавжудлигини текшириш
    cursor.execute('''
    SELECT id FROM group_admins 
    WHERE user_id = ? AND group_id = ?
    ''', (target_user.id, message.chat.id))
    
    existing_admin = cursor.fetchone()
    
    if existing_admin:
        await message.reply(f"❌ <b>{target_user.full_name}</b> аллақачон администратор!")
        conn.close()
        return
    
    # Янги администратор
    cursor.execute('''
    INSERT INTO group_admins (user_id, group_id, added_by)
    VALUES (?, ?, ?)
    ''', (target_user.id, message.chat.id, message.from_user.id))
    
    conn.commit()
    conn.close()
    
    await message.reply(TEXTS["admin_added"].format(user=target_user.full_name))

# ==============================
# 🔘 Администраторни олиб ташлаш
# ==============================
@router.message(Command("removeadmin"))
async def remove_admin(message: Message):
    """Администраторни олиб ташлаш"""
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    if not message.reply_to_message:
        await message.reply(TEXTS["syntax_error"].format(syntax="/removeadmin - фойдаланувчига жавобан"))
        return
    
    target_user = message.reply_to_message.from_user
    
    conn = get_group_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM group_admins 
    WHERE user_id = ? AND group_id = ?
    ''', (target_user.id, message.chat.id))
    
    if cursor.rowcount > 0:
        conn.commit()
        await message.reply(TEXTS["admin_removed"].format(user=target_user.full_name))
    else:
        await message.reply(f"❌ <b>{target_user.full_name}</b> администратор эмас!")
    
    conn.close()

# ==============================
# 🔘 Администраторлар рўйхати
# ==============================
@router.message(Command("admins"))
async def list_admins(message: Message):
    """Администраторлар рўйхати"""
    conn = get_group_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT user_id FROM group_admins 
    WHERE group_id = ?
    ''', (message.chat.id,))
    
    admin_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not admin_ids:
        await message.reply(TEXTS["no_admins"])
        return
    
    admins_text = ""
    for user_id in admin_ids:
        try:
            user = await message.bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "Нет username"
            admins_text += f"👑 {user.full_name} ({username})\n"
        except Exception as e:
            admins_text += f"👑 ID: {user_id} (не удалось получить информацию)\n"
    
    await message.reply(TEXTS["admin_list"].format(admins=admins_text))

# ==============================
# ==============================
# ==============================
# ==============================
# 🔘 Команда /admin
# ==============================
@router.message(Command("admin"))
async def admin_command(message: Message):
    """Админ панелини кўрсатиш"""
    if not await is_global_admin(message.from_user.id):
        await message.reply(TEXTS["no_permission"])
        return
    
    # Админ панелини кўрсатиш
    text = "👑 <b>Гуруҳ администратор панели</b>\n\n" \
           "🛠 <b>Мўлжалланган командалар:</b>\n" \
           "• /ban - Фойдаланувчини бан қилиш\n" \
           "• /kick - Фойдаланувчини чиқариш\n" \
           "• /mute - Фойдаланувчини овозсизлантириш\n" \
           "• /unmute - Овозини қайтариш\n" \
           "• /del - Хабарни ўчириш\n" \
           "• /note - Эслатма қўшиш\n" \
           "• /delnote - Эслатмани ўчириш\n" \
           "• /notes - Эслатмаларни кўрсатиш\n" \
           "• /addadmin - Администратор қўшиш\n" \
           "• /removeadmin - Администраторни олиб ташлаш\n" \
           "• /admins - Администраторлар рўйхати\n" \
           "• /broadcast - Хабар тарқатиш\n" \
           "• /help - Ёрдам маълумотлари"
    
    await message.reply(text)

# ==============================
# 🔘 Улучшенная команда /help
# ==============================
@router.message(Command("help"))
async def help_command(message: Message):
    """Ёрдам маълумотлари"""
    help_text = """
🤖 <b>Бот Ёрдам Маълумотлари:</b>

👮 <b>Модерация:</b>
• /ban [сабаб] - Фойдаланувчини бан қилиш (жавобан)
• /kick [сабаб] - Фойдаланувчини чиқариб юбориш (жавобан)
• /mute [вақт] [сабаб] - Фойдаланувчини овозсизлантириш (жавобан)
• /unmute - Фойдаланувчи овозини қайтариш (жавобан)
• /del - Хабарни ўчириш (жавобан)

📝 <b>Эслатмалар:</b>
• /note [триггер] [матн] - Янги эслатма қўшиш
• /delnote [ID] - Эслатмани ўчириш
• /notes - Барча эслатмаларни кўрсатиш
• !триггер - Эслатмани чақириш

👑 <b>Администраторлар:</b>
• /addadmin - Администратор қўшиш (жавобан)
• /removeadmin - Администраторни олиб ташлаш (жавобан)
• /admins - Администраторлар рўйхати
• /admin - Админ панелини кўрсатиш

📢 <b>Бошқа:</b>
• /broadcast [матн] - Хабар тарқатиш
• /help - Ёрдам маълумотлари

💡 <b>Эслатма:</b> Барча командалар фақат администраторлар учун!
    """
    
    await message.reply(help_text)

# Базани инициализация қилиш
init_group_db()