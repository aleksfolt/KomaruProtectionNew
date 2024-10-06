from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    add_or_del = State()


raid_alert_active = False
raid_start_time = None
raider_count = 0