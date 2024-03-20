from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
from data.config import load_config
from filters import PrivateChatFilter
from filters.user_chat import UserBanFilter, UserRegFilter
from keyboards.users.kb_menu_user import kb_user_main

router = Router(name='user_start')
config = load_config('.env')  # Load the configuration from .env file


# РОУТЕР ПО КОМАНДЕ /start
@router.message(CommandStart(), PrivateChatFilter(), UserRegFilter(), UserBanFilter())
async def start(message: Message) -> None:
    """
    Handles the /start command for new registered and non-banned users.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    """
    await message.answer(
        f'👋🏻 Приветствую тебя @<b><a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a></b>!\n\n'
        f'Я бот ChatGPT 🤖, выбери модель GPT, напиши свой вопрос и я отвечу тебе!',
        reply_markup=kb_user_main.as_markup())

