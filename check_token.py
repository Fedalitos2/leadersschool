import os, aiohttp, asyncio

async def main():
    token = os.getenv("BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as resp:
                print("Status:", resp.status)
                print("Body:", await resp.text())
        except Exception as e:
            print("Error:", e)

asyncio.run(main())
