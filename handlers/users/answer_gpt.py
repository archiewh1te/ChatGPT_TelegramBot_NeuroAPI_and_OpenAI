import asyncio
from asyncio import sleep

import aiofiles
import openai
from aiogram.fsm.context import FSMContext

from data.config import load_config
from aiogram import Router, Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.function.user_commands import select_user
from filters import PrivateChatFilter
from filters.user_chat import UserBanFilter
from handlers.users.generate_gpt import get_chatgpt
from state.AntiSpam_chatgpt import AntiFlood_gpt

router = Router(name='gpt_answer')

config = load_config('.env')

DEV_ID = config.tg_bot.dev_id  # получаем из переменной в .env


@router.message(PrivateChatFilter(), AntiFlood_gpt.generating_message)
async def anti_flood(message: Message, state: FSMContext) -> None:
    """
    Handles anti-flooding mechanism to prevent rapid message generation.

    :param message: The message object representing the user's message.
    :type message: aiogram.types.Message
    :param state: FSMContext object for managing conversation state.
    :type state: aiogram.fsm.FSMContext
    """
    await message.answer('⛔️ Вы еще не получили ответа!')


@router.message(PrivateChatFilter(), UserBanFilter())
async def chatgpt_answer(message: Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    """
    Handles the response from the GPT model to a user's message.

    :param message: The message object representing the user's message.
    :type message: aiogram.types.Message
    :param session: AsyncSession for database interactions.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    :param state: FSMContext object for managing conversation state.
    :type state: aiogram.fsm.FSMContext
    :param bot: The Bot instance for sending messages.
    :type bot: aiogram.Bot
    """
    try:
        if message.text and not message.text.startswith('/'):
            await state.set_state(AntiFlood_gpt.generating_message)
            async with aiofiles.open(file='logs/chat_logs.txt', mode='a+', encoding='utf-8') as file:
                await file.write(
                    f'Дата: {message.date} ChatId: {message.chat.id} и UserId: {message.from_user.id} '
                    f'Юзернейм: {message.from_user.username} Сообщение: {message.text}\n')

                info_msg = await message.answer('🔄 Собираю информацию.....')

                msg_for_user = await get_chatgpt(message=message, msg_for_openai=message.text, session=session)
                await sleep(0.33)
                await info_msg.delete()
                await message.answer(msg_for_user)
                await state.clear()

    except Exception as e:
        user = await select_user(user_id=message.from_user.id, session=session)
        await bot.send_message(DEV_ID,
                               f'⚠️ Случилась <b>ошибка</b> в чате @<b><a href="tg://user?id={user.user_id}">{user.first_name}</a></b>\nСтатус ошибки: <code>{e}</code>')
        await message.answer(f"❗️ Упс! <b>Ошибка!</b> Не переживайте, ошибка уже <b>отправлена</b> разработчику.❗️")
        await state.clear()
    except openai.APIConnectionError as e:
        await bot.send_message(DEV_ID, f'⚠️ {e}')
    except openai.APIStatusError as e:
        await bot.send_message(DEV_ID, f'⚠️ {e}')

        async with aiofiles.open(file='logs/chat_logs.txt', mode='a+', encoding='utf-8') as file:
            await file.write(
                f'Дата: {message.date} ChatId: {message.chat.id} и UserId: {message.from_user.id} '
                f'Юзернейм: {message.from_user.username} Сообщение: {message.text}\n')


async def main():
    await router.process_updates()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

