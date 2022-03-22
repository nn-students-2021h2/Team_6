from interface.but_folder.buttons import *


# ReplyKeyboardsMarkup
# start_markup
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_markup.add(icecream_button, help_button)
start_markup.row(image_button)

# filters_markup
filters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
filters_markup.row(button_sourse)
filters_markup.add(button_negative, button_gamma, button_gray,
                   button_shift, button_color_range, button_pixel,
                   button_cartoon, button_morph, button_sobel)
filters_markup.row(button_tired)
# baby_help_markup
baby_help_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
baby_help_markup.add(button_dark, button_light)
baby_help_markup.row(button_enough)

# colors_markup
colors_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
colors_markup.add(button_green, button_red, button_yellow, button_orange, button_lightblue, button_blue, button_purple)

# morph_markup
morph_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
morph_markup.add(button_open, button_grad, button_blackhat)

# morph_set_prof_markup
set_prof_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
set_prof_markup.add(button_set_prof)
set_prof_markup.row(button_enough)
