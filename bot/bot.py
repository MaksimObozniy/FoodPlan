import os
import asyncio
import sys
from dotenv import load_dotenv


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlan.settings')
import django
django.setup()


from aiogram import Bot, Dispatcher
from handlers import router


load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())