import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from storage import storage

# 🔹 Bot token
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=storage)

# 🔹 HTTP сервер для health checks
async def handle_health_check(request):
    return web.Response(text="✅ Bot is alive and running!")

async def start_http_server():
    """Запуск HTTP сервера для Render"""
    app = web.Application()
    app.router.add_get('/', handle_health_check)
    app.router.add_get('/health', handle_health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Используем порт из переменной окружения или 8080 по умолчанию
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    print(f"✅ HTTP server started on port {port}")
    return runner

async def main():
    # 🔹 Запускаем HTTP сервер
    http_runner = await start_http_server()
    
    # 🔹 Импортируем и подключаем роутеры
    from handlers.admin import router as admin_router
    from handlers.start import router as start_router
    from handlers.courses import router as courses_router
    from handlers.schedule import router as schedule_router
    from handlers.register import router as register_router
    from handlers.reviews import router as reviews_router
    from handlers.contacts import router as contacts_router
    from handlers.language import router as language_router
    from handlers.question import router as question_router
    from handlers.group_moderation import router as group_moderation_router
    from handlers.broadcast import router as broadcast_router
    from handlers.group_register import router as group_register_router

    dp.include_router(admin_router)
    dp.include_router(question_router)
    dp.include_router(start_router)
    dp.include_router(courses_router)
    dp.include_router(schedule_router)
    dp.include_router(register_router)
    dp.include_router(reviews_router)
    dp.include_router(contacts_router)
    dp.include_router(language_router)
    dp.include_router(group_moderation_router)
    dp.include_router(broadcast_router)
    dp.include_router(group_register_router)


    # 🔹 Инициализация БД
    from data.db import init_db
    init_db()
    
    # 🔹 Инициализация группы БД
    from handlers.group_moderation import init_group_db
    init_group_db()

    print("✅ Bot ishga tushdi...")
    
    try:
        await dp.start_polling(bot)
    finally:
        # Корректное завершение
        await http_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())