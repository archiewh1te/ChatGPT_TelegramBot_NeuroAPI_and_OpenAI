import datetime

from aiogram import Router
from aiogram.types import Message
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import load_config
from database.function.server_commands import select_all_gpt_endpoint
from database.function.user_commands import select_user

router = Router(name='generate_chatgpt')

config = load_config('.env')

DEV_ID = config.tg_bot.dev_id  # получаем из переменной в .env

API_KEY = config.tg_bot.openai_api_key  # получаем из переменной в .env


async def get_chatgpt(message: Message, session: AsyncSession, msg_for_openai: str) -> str:
    """
    Generate a response from the ChatGPT model based on the user's message.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    :param session: AsyncSession for database interactions.
    :type session: sqlalchemy.ext.asyncio.AsyncSession
    :param msg_for_openai: The message content to be sent to the OpenAI API for processing.
    :type msg_for_openai: str
    :return: The generated response from the ChatGPT model.
    :rtype: str
    """

    all_endpoint = await select_all_gpt_endpoint(session=session)
    for server in all_endpoint:
        client = AsyncOpenAI(api_key=API_KEY, base_url=server.endpoint)

        current_time = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
        system_prompt = f"Текущее время: {current_time}. "

        user = await select_user(user_id=message.from_user.id, session=session)
        chat_completion = await client.chat.completions.create(
            model=f"{user.gpt_model}",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg_for_openai},
            ],
            temperature=0.7,
            max_tokens=4000,
            stream=True,
            timeout=30
        )

        response = ""  # Переменная для накопления ответа
        async for chunk in chat_completion:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content  # Накопление ответа
        if not response:  # Проверка, содержит ли response какие-либо данные
            response = "❌ Извините, не удалось получить ответ от модели AI, повторите запрос."
        return response
