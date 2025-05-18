from aiogram import Bot, Dispatcher
import logging
from dotenv import load_dotenv
import os
import asyncio
from handlers import start_handler


load_dotenv()


async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(start_handler.router, )
    logging.basicConfig(level=logging.INFO)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())