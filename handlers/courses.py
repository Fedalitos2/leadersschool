from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.main_menu import main_menu
from keyboards.courses_menu import courses_menu
from data.languages import user_languages

router = Router()

# ---------------------------
# Список курсов по направлениям
# ---------------------------
# ---------------------------
# Список курсов по направлениям
# ---------------------------
def course_list(direction: str, lang: str = "ru") -> str:
    texts = {
        "uy_hamshiralik": {
            "ru": "🏠 <b>Уй Хамширалик:</b>\n\nПрофессиональное обучение домашнему уходу и медицинскому обслуживанию на дому. Идеально для тех, кто хочет работать в сфере домашнего ухода за больными и пожилыми людьми.",
            "uz": "🏠 <b>Uy Hamshiralik:</b>\n\nUy davolash va tibbiy xizmat ko'rsatish bo'yicha professional ta'lim. Kasal va keksa odamlarga g'amxo'rlik qilish sohasida ishlashni xohlaydiganlar uchun ideal.",
            "en": "🏠 <b>Home Nursing:</b>\n\nProfessional training in home care and medical services at home. Ideal for those who want to work in the field of home care for the sick and elderly."
        },
        "english": {
            "ru": "🌍 <b>Английский язык:</b>\n\nОбучение английскому языку для всех уровней - от начального до продвинутого. Подготовка к международным экзаменам, разговорная практика, грамматика и лексика.",
            "uz": "🌍 <b>Ingliz tili:</b>\n\nBoshlang'ichdan ilg'or darajagacha bo'lgan barcha darajalar uchun ingliz tili o'qitish. Xalqaro imtihonlarga tayyorgarlik, suhbat amaliyoti, grammatika va leksika.",
            "en": "🌍 <b>English Language:</b>\n\nEnglish language teaching for all levels - from beginner to advanced. Preparation for international exams, conversation practice, grammar and vocabulary."
        },
        "biology": {
            "ru": "🔬 <b>Биология:</b>\n\nИзучение биологии для школьников и абитуриентов. Подготовка к экзаменам, олимпиадам, углубленное изучение анатомии, физиологии и молекулярной биологии.",
            "uz": "🔬 <b>Biologiya:</b>\n\nMaktab o'quvchilari va abituriyentlar uchun biologiyani o'rganish. Imtihonlar va olimpiadalarga tayyorgarlik, anatomiya, fiziologiya va molekulyar biologiyani chuqur o'rganish.",
            "en": "🔬 <b>Biology:</b>\n\nBiology study for schoolchildren and applicants. Preparation for exams and olympiads, in-depth study of anatomy, physiology and molecular biology."
        },
        "it": {
            "ru": "💻 <b>IT курсы:</b>\n\nОбучение программированию, веб-разработке, графическому дизайну и кибербезопасности. Современные технологии и практические навыки для IT-специалистов.",
            "uz": "💻 <b>IT kurslari:</b>\n\nDasturlash, veb-dasturlash, grafik dizayn va kiberxavfsizlikni o'qitish. IT mutaxassislari uchun zamonaviy texnologiyalar va amaliy ko'nikmalar.",
            "en": "💻 <b>IT Courses:</b>\n\nTeaching programming, web development, graphic design and cybersecurity. Modern technologies and practical skills for IT specialists."
        },
        "russian": {
            "ru": "🌍 <b>Русский язык:</b>\n\nИзучение русского языка для разных уровней. Грамматика, разговорная речь, подготовка к экзаменам. Для начинающих и продвинутых студентов.",
            "uz": "🌍 <b>Rus tili:</b>\n\nTurli darajalar uchun rus tilini o'rganish. Grammatika, og'zaki nutq, imtihonlarga tayyorgarlik. Boshlang'ich va ilg'or talabalar uchun.",
            "en": "🌍 <b>Russian Language:</b>\n\nLearning Russian for different levels. Grammar, conversation, exam preparation. For beginner and advanced students."
        },
        "math": {
            "ru": "🧮 <b>Математика:</b>\n\nОбучение математике для школьников всех классов. Подготовка к экзаменам, олимпиадная математика, решение сложных задач и развитие логического мышления.",
            "uz": "🧮 <b>Matematika:</b>\n\nBarcha sinf maktab o'quvchilari uchun matematikani o'qitish. Imtihonlarga tayyorgarlik, olimpiada matematikasi, murakkab masalalarni yechish va mantiqiy fikrlashni rivojlantirish.",
            "en": "🧮 <b>Mathematics:</b>\n\nTeaching mathematics for schoolchildren of all grades. Exam preparation, olympiad mathematics, solving complex problems and developing logical thinking."
        },
        "arabic": {
            "ru": "🌍 <b>Арабский язык:</b>\n\nИзучение арабского языка и культуры. Арабская письменность, грамматика, разговорная практика. Для начинающих и продолжающих изучение.",
            "uz": "🌍 <b>Arab tili:</b>\n\nArab tili va madaniyatini o'rganish. Arab yozuvi, grammatika, og'zaki nutq amaliyoti. Boshlang'ich va davom etuvchilar uchun.",
            "en": "🌍 <b>Arabic Language:</b>\n\nLearning Arabic language and culture. Arabic writing, grammar, conversation practice. For beginners and continuing students."
        },
        "president": {
            "ru": "🎓 <b>Подготовка в Президентскую школу:</b>\n\nКомплексная подготовка к поступлению в Президентские школы. Математика, логика, английский язык, тестирование и собеседование.",
            "uz": "🎓 <b>Prezident maktabiga tayyorlov:</b>\n\nPrezident maktablariga kirish uchun kompleks tayyorgarlik. Matematika, mantiq, ingliz tili, testlash va suhbat.",
            "en": "🎓 <b>Presidential School Preparation:</b>\n\nComprehensive preparation for admission to Presidential schools. Mathematics, logic, English language, testing and interview."
        }
    }
    return texts[direction][lang]

# ---------------------------
## ---------------------------
# Обработка кнопки "📚 Курсы"
# ---------------------------
@router.callback_query(lambda c: c.data in ["courses", "dir_uy_hamshiralik", "dir_english", "dir_biology", "dir_it", 
                                           "dir_russian", "dir_math", "dir_arabic", "dir_president", "back_main"])
async def courses_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = user_languages.get(user_id, "ru")  # по умолчанию русский
    data = call.data

    if data == "courses":
        texts = {
            "ru": "📚 <b>Выберите направление:</b>",
            "uz": "📚 <b>Yo'nalishni tanlang:</b>",
            "en": "📚 <b>Choose a direction:</b>"
        }
        await call.message.answer(texts[lang], reply_markup=courses_menu(lang))
    
    elif data in ["dir_uy_hamshiralik", "dir_english", "dir_biology", "dir_it", 
                 "dir_russian", "dir_math", "dir_arabic", "dir_president"]:
        direction = data.split("_")[1]
        await call.message.answer(course_list(direction, lang), reply_markup=courses_menu(lang))
    
    elif data == "back_main":
        greetings = {
            "ru": "🏠 Главное меню:",
            "uz": "🏠 Asosiy menyu:",
            "en": "🏠 Main menu:"
        }
        await call.message.answer(greetings[lang], reply_markup=main_menu(lang))

    await call.answer()  # убираем "часики" при нажатии