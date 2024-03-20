from aiogram.fsm.state import StatesGroup, State


# Изменить статус подписки
class send_to_subscription(StatesGroup):
    text = State()
    state = State()
