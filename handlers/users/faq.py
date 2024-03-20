from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from filters import PrivateChatFilter
from keyboards.users.kb_menu_user import kb_back

router = Router(name='faq')


@router.message(PrivateChatFilter(), Command("faq"))
async def get_faq(message: types.Message) -> None:
    """
    Handles the "/faq" command to provide Frequently Asked Questions (FAQ).

    :param message: The Message object representing the user's message.
    :type message: aiogram.types.Message
    """
    await message.reply(f'<b>Какие модели ChatGPT доступны ❓</b>\n\n'
                        'gpt-3.5-turbo\n\n'
                        'gpt-3.5-turbo-0613\n\n'
                        'gpt-3.5-turbo-1106\n\n'
                        'gpt-3.5-turbo-16k\n\n'
                        'gpt-3.5-turbo-16k-0613\n\n'
                        'gpt-4\n\n'

                        '<b>Как сменить модель ChatGPT ❓</b>\n\n'

                        'Для того чтобы сменить модель, нажмите кнопку\n<b>🤖 Сменить модель GPT</b> и выберите '
                        ' нужную из '
                        'доступных моделей.\n\n'

                        '<b>Что делать при ошибках после того как сделал запрос ❓</b>\n\n'

                        '1. Повторить запрос.\n\n'
                        '2. Сменить GPT и повторить запрос.\n\n'
                        '3. Обратиться в <b>support</b>.\n\n'

                        '<b>Что такое подписка ❓</b>\n\n'

                        'Подписка даёт возможность пользоваться моделями ChatGPT\n\n'

                        '<b>Как обратиться в службу поддержки ❓</b>\n\n'

                        'Чтобы обратиться в службу поддержки, нужно нажать на кнопку <b>✉️ Написать в '
                        'support</b> оставить своё обращение, после этого с вами свяжутся.',
                        disable_web_page_preview=True
                        )


@router.callback_query(F.data.startswith("userfaq"), PrivateChatFilter())
async def user_profile(call: CallbackQuery) -> None:
    """
    Handles the FAQ button callback to provide Frequently Asked Questions (FAQ).

    :param call: The CallbackQuery object representing the callback.
    :type call: aiogram.types.CallbackQuery
    """
    await call.answer(cache_time=5)
    await call.message.edit_text(
        f'<b>Какие модели ChatGPT доступны ❓</b>\n\n'

        'gpt-3.5-turbo\n\n'
        'gpt-3.5-turbo-0613\n\n'
        'gpt-3.5-turbo-1106\n\n'
        'gpt-3.5-turbo-16k\n\n'
        'gpt-3.5-turbo-16k-0613\n\n'
        'gpt-4\n\n'

        '<b>Как сменить модель ChatGPT ❓</b>\n\n'

        'Для того чтобы сменить модель, нажмите кнопку\n<b>🤖 Сменить модель GPT</b> и '
        ' выберите'
        ' нужную из '
        'доступных моделей.\n\n'

        '<b>Что делать при ошибках после того как сделал запрос ❓</b>\n\n'

        '1. Повторить запрос.\n\n'
        '2. Сменить GPT и повторить запрос.\n\n'
        '3. Обратиться в <b>support</b>.\n\n'

        '<b>Что такое подписка ❓</b>\n\n'

        'Подписка даёт возможность пользоваться моделями ChatGPT.\n\n'

        '<b>Как обратиться в службу поддержки ❓</b>\n\n'

        'Чтобы обратиться в службу поддержки, нужно нажать на кнопку <b>✉️ Написать в '
        'support</b> оставить своё обращение, после этого с вами свяжутся.',
        disable_web_page_preview=True,
        reply_markup=kb_back.as_markup())
