from aiogram.dispatcher.filters.state import State, StatesGroup


class StartManagment(StatesGroup):
    ice_cream_not_done = State()
    ice_cream_done = State()


class ImageDownload(StatesGroup):
    download_not_complete = State()
    download_done = State()


class Filters(StatesGroup):
    meanshift_working = State()
    color_range_working = State()
    morph_choosing_working = State()
    pixel_working = State()


class Gamma_filter(StatesGroup):
    gamma_start = State()
    gamma_1 = State()


class MorphManagment(StatesGroup):
    blackhat_working = State()
    open_working = State()
    grad_working = State()
