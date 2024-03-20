from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from filters import PrivateChatFilter
from keyboards.users.kb_menu_user import kb_back

router = Router(name='helps')


@router.message(PrivateChatFilter(), Command("help"))
async def get_help(message: types.Message) -> None:
    """
    Handles the "/help" command to provide help and guidelines for using the ChatGPT model.

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    """
    await message.reply(f'<b>Как это работает ❓</b>\n\n'
                        'Вы можете задавать GPT вопросы, и он постарается дать вам на них ответ, исходя из своих '
                        'знаний.\n\n'

                        '<b>Как получить качественный результат ❓</b>\n\n'

                        '1. Формулируйте вопрос так, чтобы он был ясным и конкретным.\n\n'

                        '2. Включайте в вопрос ключевые слова, связанные с вашей темой.\n\n'

                        '3. Если модель не улавливает полностью ваш контекст или нужду в ответе, попробуйте '
                        'предоставить дополнительные детали или объяснения. Это поможет модели лучше понять ваш '
                        'запрос и дать более релевантный ответ.\n\n'

                        '4. Указывайте числа или параметры, если это необходимо.\n')


@router.callback_query(F.data.startswith("userhelp"), PrivateChatFilter())
async def user_profile(call: CallbackQuery) -> None:
    """
    Handles the Help button callback to provide help and guidelines for using the ChatGPT model.

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    """
    await call.answer(cache_time=5)
    await call.message.edit_text(f'<b>Как это работает ❓</b>\n\n'
                                 'Вы можете задавать GPT вопросы, и он постарается дать вам на них ответ, исходя из '
                                 'своих знаний\n\n'

                                 '<b>Как получить качественный результат ❓</b>\n\n'

                                 '1. Формулируйте вопрос так, чтобы он был ясным и конкретным.\n\n'

                                 '2. Включайте в вопрос ключевые слова, связанные с вашей темой.\n\n'

                                 '3. Если модель не улавливает полностью ваш контекст или нужду в ответе, попробуйте '
                                 'предоставить дополнительные детали или объяснения. Это поможет модели лучше понять '
                                 'ваш запрос и дать более релевантный ответ.\n\n'

                                 '4. Указывайте числа или параметры, если это необходимо.\n',
                                 reply_markup=kb_back.as_markup())

