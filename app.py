import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook

from database.function.setup import create_engine, sync_database_tables, create_session_pool
from data.config import load_config, Config
from handlers.admins import start_admin
from handlers.admins.admin_panel import download_logs, panels, unbans, edit_tokens, subscription, bans, all_users, \
    add_models, delete_models, clear_all_logs, notice_to_users
from handlers.users import user_start, helps, about, answer_gpt, profile, faq, change_gpt_model, support, generate_gpt
from middlewares import ConfigMiddleware, DatabaseMiddleware
from middlewares.throttling import ThrottlingMiddleware

from utils.commands import set_default_commands
from utils.notify_admins import on_startup_notify, notify_start_PSQL

logger = logging.getLogger(__name__)


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool):
    """
    Registers global middlewares for the bot.

    :param dp: Dispatcher object of the bot.
    :type dp: aiogram.Dispatcher
    :param config: Configuration object of the bot.
    :type config: data.config.Config
    :param session_pool: Session Pool object created by SQLAlchemy.
    :type session_pool: sqlalchemy.orm.session.SessionPool
    """
    dp.update.outer_middleware(ConfigMiddleware(config))
    dp.update.outer_middleware(DatabaseMiddleware(session_pool))


async def main():
    logger.info('Starting bot...')

    config = load_config('.env')  # Load the configuration from .env file
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    engine = create_engine(db=config.db, echo=True)
    await sync_database_tables(engine=engine, drop_tables=False)
    session_pool = create_session_pool(engine=engine)

    bot.config = config  # Binding the bot config to the bot object
    bot.db = session_pool  # Binding the session pool of the bot to the bot object

    await set_default_commands(bot)
    await on_startup_notify(bot)
    await notify_start_PSQL(bot)
    import utils.logging

    # Registering bot middlewares
    register_global_middlewares(dp=dp, config=config, session_pool=session_pool)
    dp.message.middleware(ThrottlingMiddleware())  # Registration of middleware

    try:
        # Connection of handlers to the bot
        dp.include_routers(
            start_admin.router,
            all_users.router,
            bans.router,
            unbans.router,
            edit_tokens.router,
            notice_to_users.router,
            download_logs.router,
            clear_all_logs.router,
            panels.router,
            user_start.router,
            profile.router,
            subscription.router,
            about.router,
            change_gpt_model.router,
            helps.router,
            faq.router,
            support.router,
            generate_gpt.router,
            add_models.router,
            delete_models.router,

            answer_gpt.router,  # Should be last

        )
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
