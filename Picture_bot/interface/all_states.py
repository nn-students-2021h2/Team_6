from aiogram.dispatcher.filters.state import State, StatesGroup


class StartManagment(StatesGroup):
    ice_cream_not_done = State()
    ice_cream_done = State()


class ImageDownload(StatesGroup):
    download_not_complete = State()
    download_done = State()


class Filters(StatesGroup):
    color_range_working = State()
    gamma_working = State()
    morph_choosing_working = State()


class MorphManagment(StatesGroup):
    morphling_working = State()
    mosaic_working = State()
    border_working = State()
