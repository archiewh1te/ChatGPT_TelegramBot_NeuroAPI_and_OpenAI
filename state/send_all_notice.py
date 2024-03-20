from aiogram.fsm.state import StatesGroup, State


# Уведомления для всех юзеров
class send_notice_allusers(StatesGroup):
    text = State()
    state = State()
    photo = State()