from aiogram import types


# KeyboardButton
# for start menu
start_buttons = ["🍧 Хочу мороженку", "🎨 Мне нужно обработать изображение"]

# filters list
button_sourse = types.KeyboardButton("Исходник")
button_negative = types.KeyboardButton("Негатив")
button_gamma = types.KeyboardButton("Гамма Фильтр")
button_gray = types.KeyboardButton("Черно-белый")
button_shift = types.KeyboardButton("Средний сдвиг")
button_color_range = types.KeyboardButton("Цветовой диапазон")
button_pixel = types.KeyboardButton("Пикселизация")
button_tired = types.KeyboardButton("Я устал")

# for gamma filter work
button_dark = types.KeyboardButton("0.5 Немного затемнить")
button_light = types.KeyboardButton("1.5 Немного осветлить")
button_enough = types.KeyboardButton("Перестань (reset brightnes)")

# for colour list
button_green = types.KeyboardButton("Зелёный")
button_red = types.KeyboardButton("Красный")
button_orange = types.KeyboardButton("Оранжевый")
button_yellow = types.KeyboardButton("Жёлтый")
button_lightblue = types.KeyboardButton("Голубой")
button_blue = types.KeyboardButton("Синий")
button_purple = types.KeyboardButton("Фиолетовый")

# InlineKeyboardButton
# 18 years old menu buttons
button_yes = types.InlineKeyboardButton(text = "Да", callback_data = "years_old_18")
button_no = types.InlineKeyboardButton(text = "Нет", callback_data = "years_old_not_18")