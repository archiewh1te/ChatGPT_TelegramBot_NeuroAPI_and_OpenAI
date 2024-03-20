from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import load_config
from database.function.user_commands import select_user
from filters import PrivateChatFilter

from aiogram import Router, F

from aiogram.types import Message, CallbackQuery

from keyboards.users.kb_menu_user import kb_back, kb_user_main

config = load_config('.env')

DEV_ID = config.tg_bot.dev_id

router = Router(name='profile')


# РОУТЕР ПО КОМАНДЕ /profile
@router.message(Command('profile'), PrivateChatFilter())
async def profile(message: Message, session: AsyncSession) -> None:
    """
    Handles the "/profile" command to display user profile with subscription information.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    """
    user = await select_user(user_id=message.from_user.id, session=session)

    if user.subscription == "active":
        subscription_text = "✅ Активная"
    else:
        subscription_text = "❌ Заблокированная"  # Если подписка не "active"
    await message.answer(text='📊 <b>Ваш профиль:</b>\n\n'
                              
                              f'👤 <b>Имя:</b> {user.first_name} \n'
                              f'🖥 <b>ID:</b> <code>{user.user_id}</code>\n\n'
                              
                              f'💎 <b>Подписка:</b> {subscription_text}\n'
                              f'🤖 <b>Модель GPT:</b> {user.gpt_model} \n\n'
                              
                              '❓ <i>Как это работает</i> - <b>/help</b> \n\n'
                              '❓ <i>Как пользоваться</i> - <b>/faq</b>')


# РОУТЕР КНОПКИ ПРОФИЛЬ
@router.callback_query(F.data.startswith("userprofile"), PrivateChatFilter())
async def user_profile(call: CallbackQuery, session: AsyncSession) -> None:
    """
    Handles the User Profile button callback to display user profile with subscription information.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    :param session: The AsyncSession object for asynchronous database operations.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    """
    await call.answer()
    user = await select_user(user_id=call.from_user.id, session=session)

    if user.subscription == "active":
        subscription_text = "✅ Активная"
    else:
        subscription_text = "❌ Заблокированная"  # Если подписка не "active"
    await call.message.edit_text(text='📊 <b>Ваш профиль:</b>\n\n'
                                      
                                      f'👤 <b>Имя:</b> {user.first_name}\n'
                                      f'🖥 <b>ID:</b> <code>{user.user_id}</code>\n\n'
                                      
                                      f'💎 <b>Подписка:</b> {subscription_text}\n'
                                      f'🤖 <b>Модель GPT:</b> {user.gpt_model}\n\n'
                                      
                                      '❓ <i>Как это работает</i> - <b>/help</b>\n\n'
                                      '❓ <i>Как пользоваться</i> - <b>/faq</b>', reply_markup=kb_back.as_markup())


# РОУТЕР КНОПКИ НАЗАД
@router.callback_query(F.data.startswith("back"), PrivateChatFilter())
async def get_back(call: CallbackQuery) -> None:
    """
    Handles the Back button callback to return to the main menu.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    """
    await call.answer()
    await call.message.edit_text(
        f'👋🏻 Приветствую тебя @<b><a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a></b>!\n\n'
        f'Я бот ChatGPT 🤖, выбери модель GPT, напиши свой вопрос и я отвечу тебе!',
        reply_markup=kb_user_main.as_markup())
