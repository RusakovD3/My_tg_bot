from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import executor
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


class Form(StatesGroup):
    waiting_for_letter = State()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
    "Отправить анонимное письмо",
    "Получить рандомную фразу",
    "Получить рандомную картинку",
]
keyboard.add(*buttons)


async def create_db_pool():
    return await asyncpg.create_pool(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME
    )


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Выберите действие если хотите провзаимодействовать с ботом, а если не хотите, то зачем вы здесь..?",
        reply_markup=keyboard,
    )


@dp.message_handler(lambda message: message.text == "Отправить анонимное письмо")
async def anonymous_letter(message: types.Message):
    await Form.waiting_for_letter.set()
    await message.answer("Напишите письмо: (возможно я даже отвечу на него)")


@dp.message_handler(state=Form.waiting_for_letter)
async def process_letter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["letter"] = message.text
    with open("letters.txt", "a", encoding="utf8") as file:
        file.write(
            f"Автор: {message.from_user.id}, Дата: {message.date}, Содержание: {data['letter']}\n"
        )
    await message.answer("Ваше письмо сохранено. (если сервер не упал..)")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Получить рандомную фразу")
async def random_phrase(message: types.Message):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        phrase = await conn.fetchval(
            "SELECT text FROM phrase ORDER BY RANDOM() LIMIT 1"
        )
    await message.answer(phrase)


@dp.message_handler(lambda message: message.text == "Получить рандомную картинку")
async def random_image(message: types.Message):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        image = await conn.fetchval(
            "SELECT image FROM images ORDER BY RANDOM() LIMIT 1"
        )
    await message.reply_photo(image)


@dp.message_handler()
async def send(message: types.Message):
    await message.answer("Пункт не выбран.")


if __name__ == "__main__":
    executor.start_polling(dp)
