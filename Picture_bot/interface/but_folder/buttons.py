from aiogram import types


# KeyboardButton
# for start menu
icecream_button = "🍧 Хочу мороженку"
image_button = "🎨 Мне нужно обработать изображение"
help_button = "🕵‍♂️Что ты умеешь?"

# filters list
button_sourse = types.KeyboardButton("Исходник")
button_negative = types.KeyboardButton("Негатив")
button_gamma = types.KeyboardButton("Гамма Фильтр")
button_gray = types.KeyboardButton("Черно-белый")
button_shift = types.KeyboardButton("Средний сдвиг")
button_color_range = types.KeyboardButton("Цветовой диапазон")
button_pixel = types.KeyboardButton("Пикселизация")
button_cartoon = types.KeyboardButton("Мультиколизация")
button_grad = types.KeyboardButton("Градиент")
button_open = types.KeyboardButton("Открытие")
button_blackhat = types.KeyboardButton("Черная шляпа")
button_morph_set_prof = types.KeyboardButton("Поработай")
button_morph = types.KeyboardButton("Морфология")
button_sobel = types.KeyboardButton("Выделить границы")
button_tired = types.KeyboardButton("Я устал")

# for gamma filter work
button_dark = types.KeyboardButton("0.5 Немного затемнить")
button_light = types.KeyboardButton("1.5 Немного осветлить")
button_enough = types.KeyboardButton("Перестань")

# for pixel filter
button_2 = types.KeyboardButton("2")
button_4 = types.KeyboardButton("4")
button_8 = types.KeyboardButton("8")
button_16 = types.KeyboardButton("16")
button_32 = types.KeyboardButton("32")

# for colour list
button_green = types.KeyboardButton("Зелёный")
button_red = types.KeyboardButton("Красный")
button_orange = types.KeyboardButton("Оранжевый")
button_yellow = types.KeyboardButton("Жёлтый")
button_lightblue = types.KeyboardButton("Голубой")
button_blue = types.KeyboardButton("Синий")
button_purple = types.KeyboardButton("Фиолетовый")