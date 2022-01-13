from aiogram.dispatcher.filters.state import State, StatesGroup


class StartManagment(StatesGroup):
    ice_crem_not_done = State()
    ice_crem_done = State()

class ImageDownload(StatesGroup):
    download_not_complete = State()
    prepare_downloading = State()
    download_done = State()

class Filters(StatesGroup):
    color_range_working = State()
    gamma_working = State()
