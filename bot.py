import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

import database
import openai_service

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
if not BOT_TOKEN:
    exit("Error: BOT_TOKEN not found in .env file")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        await database.add_user(message.from_user.id, message.from_user.username)
        await message.answer("Welcome! I am an OpenAI-powered bot. Send me a message to chat.")
    else:
        await message.answer("Welcome back!")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "/start - Start the bot\n"
        "/upgrade - Upgrade to Premium\n"
        "/status - Check your status\n"
        "/help - Show this help message"
    )
    await message.answer(help_text)

@dp.message(Command("status"))
async def cmd_status(message: Message):
    user = await database.get_user(message.from_user.id)
    if user:
        status = "Premium 🌟" if user[2] else "Standard" # user[2] is is_premium
        await message.answer(f"Your status: {status}")
    else:
        await message.answer("User not found.")

@dp.message(Command("upgrade"))
async def cmd_upgrade(message: Message):
    # Mock payment / upgrade logic
    await database.set_premium(message.from_user.id, True)
    await message.answer("Congratulations! You are now a Premium user. 🌟\nYou have access to better AI models.")

@dp.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    text = message.text

    # Notify Admin
    if ADMIN_ID:
        try:
            admin_msg = f"📩 New Message from {username} (ID: {user_id}):\n\n{text}"
            await bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        except Exception as e:
            logging.error(f"Failed to notify admin: {e}")

    # Get User Status
    user = await database.get_user(user_id)
    if not user:
        await database.add_user(user_id, username)
        is_premium = False
    else:
        is_premium = bool(user[2])

    # Send 'Typing' action
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Get AI Response
    response = await openai_service.get_ai_response(text, is_premium)
    
    await message.answer(response)

async def main():
    await database.init_db()
    logging.info("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
