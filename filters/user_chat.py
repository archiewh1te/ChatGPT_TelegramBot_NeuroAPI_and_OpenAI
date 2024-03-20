from typing import Union

from aiogram import Bot
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import load_config
from database.function.user_commands import select_user_filter, select_user, create_user
from keyboards.users.kb_menu_user import kb_user_main

config = load_config('.env')  # Load the configuration from .env file


class UserBanFilter(BaseFilter):
    """ Filter that checks if a user is banned. """

    async def __call__(
            self,
            obj: Union[Message, CallbackQuery],
            session: AsyncSession
    ):

        user_id = obj.from_user.id  # Get the user ID

        if await select_user_filter(user_id=user_id, session=session, status='active'):
            return True
        else:
            await obj.answer('⛔️ Вы забанены! Данная команда не доступна ⛔️')
            raise SkipHandler()


class UserRegFilter(BaseFilter):
    """ Filter that checks if a user is registration. """

    async def __call__(
            self,
            obj: Union[Message, CallbackQuery],
            session: AsyncSession,
            bot: Bot
    ):

        if await select_user(user_id=obj.from_user.id, session=session):
            return True
        else:
            await obj.answer(
                f'👋🏻 Приветствую тебя @<b><a href="tg://user?id={obj.from_user.id}">{obj.from_user.first_name}</a></b>!\n\n'
                f'Я бот ChatGPT 🤖, выбери модель GPT, напиши свой вопрос и я отвечу тебе!',
                reply_markup=kb_user_main.as_markup())
            await create_user(session=session, user_id=obj.from_user.id,
                              first_name=obj.from_user.first_name,
                              last_name=obj.from_user.last_name,
                              status='active',
                              subscription='active',
                              tokkens='5000',
                              gpt_model='gpt-3.5-turbo',
                              access=int('0'),
                              reason='no reason', commit=True)
            await bot.send_message(chat_id=config.tg_bot.dev_id, text=f'<b>🆕 У нас новый пользователь</b>\n\n'
                                                                      f'<b>👤 NickName</b>: <b><a href="tg://user?id={obj.from_user.id}">{obj.from_user.first_name}</a></b>\n'
                                                                      f'<b>🆔 ID:</b> <code>{obj.from_user.id}</code>\n')
            return False
