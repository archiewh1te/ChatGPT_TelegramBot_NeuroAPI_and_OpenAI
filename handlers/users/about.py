from aiogram import types, Router
from aiogram.filters import Command

from filters import PrivateChatFilter

router = Router(name='about')


@router.message(PrivateChatFilter(), Command("about"))
async def get_about(message: types.Message) -> None:
    """
    Handler function for the /about command.

    :param message: The message object representing the command message.
    :type message: aiogram.types.Message
    """
    await message.reply(
        f'Я - бот с генеративным искусственным интеллектом,\n'
        f'Если у вас есть вопросы или нужна помощь, не стесняйтесь обращаться.\n\n'
        f'🧑‍💻 Бот создан @<b><a href="https://t.me/ArchieWh1te">ArchieWh1te</a></b>\n'
        f'⭐ По вопросам рекламы к @<b><a '
        f'href="https://t.me/ArchieWh1te">ArchieWh1te</a></b>', disable_web_page_preview=True)

