from interface.but_folder.buttons import *


# ReplyKeyboardsMarkup
# start_markup
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_markup.add(*start_buttons)

# filters_markup
filters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
filters_markup.add(button_sourse, button_negative, button_gamma, button_gray,
                   button_shift, button_color_range, button_pixel,
                   button_cartoon, button_tired)
# baby_help_markup
baby_help_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
baby_help_markup.add(button_dark, button_light)

# baby_enough_markup
baby_enough_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
baby_enough_markup.add(button_dark, button_light, button_enough)

# colors_markup
colors_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
colors_markup.add(button_green, button_red, button_yellow, button_orange, button_lightblue, button_blue, button_purple)
