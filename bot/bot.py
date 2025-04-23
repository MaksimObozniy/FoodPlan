import os
import django
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import router


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlan.settings')
django.setup()

load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())