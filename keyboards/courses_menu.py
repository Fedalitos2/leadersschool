from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def courses_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с направлениями курсов и кнопкой "Назад"
    lang: "ru", "uz", "en"
    """
    if lang == "ru":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Медицинская помощь дома", callback_data="dir_uy_hamshiralik")],
            [InlineKeyboardButton(text="🌍 Английский язык", callback_data="dir_english")],
            [InlineKeyboardButton(text="🔬 Биология", callback_data="dir_biology")],
            [InlineKeyboardButton(text="💻 IT", callback_data="dir_it")],
            [InlineKeyboardButton(text="🌍 Русский язык", callback_data="dir_russian")],
            [InlineKeyboardButton(text="🧮 Математика", callback_data="dir_math")],
            [InlineKeyboardButton(text="🌍 Арабский язык", callback_data="dir_arabic")],
            [InlineKeyboardButton(text="🎓 Подготовка в Президентскую школу", callback_data="dir_president")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_main")]
        ])
    elif lang == "uz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Uy Hamshiralik", callback_data="dir_uy_hamshiralik")],
            [InlineKeyboardButton(text="🌍 Ingliz tili", callback_data="dir_english")],
            [InlineKeyboardButton(text="🔬 Biologiya", callback_data="dir_biology")],
            [InlineKeyboardButton(text="💻 IT", callback_data="dir_it")],
            [InlineKeyboardButton(text="🌍 Rus tili", callback_data="dir_russian")],
            [InlineKeyboardButton(text="🧮 Matematika", callback_data="dir_math")],
            [InlineKeyboardButton(text="🌍 Arab tili", callback_data="dir_arabic")],
            [InlineKeyboardButton(text="🎓 Prezident maktabiga tayyorlov", callback_data="dir_president")],
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_main")]
        ])
    else:  # en
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Home Nursing", callback_data="dir_uy_hamshiralik")],
            [InlineKeyboardButton(text="🌍 English Language", callback_data="dir_english")],
            [InlineKeyboardButton(text="🔬 Biology", callback_data="dir_biology")],
            [InlineKeyboardButton(text="💻 IT", callback_data="dir_it")],
            [InlineKeyboardButton(text="🌍 Russian Language", callback_data="dir_russian")],
            [InlineKeyboardButton(text="🧮 Mathematics", callback_data="dir_math")],
            [InlineKeyboardButton(text="🌍 Arabic Language", callback_data="dir_arabic")],
            [InlineKeyboardButton(text="🎓 Presidential School Preparation", callback_data="dir_president")],
            [InlineKeyboardButton(text="🏠 Main menu", callback_data="back_main")]
        ])