from interface.but_folder.buttons import *


# ReplyKeyboardsMarkup
# start_markup
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
start_markup.add(*start_buttons)

# filters_markup
filters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
filters_markup.add(button_sourse, button_negative, button_gamma, button_gray,
                   button_shift, button_color_range, button_pixel,
                   button_cartoon, button_morph, button_sobel, button_tired)
# baby_help_markup
baby_help_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
baby_help_markup.add(button_dark, button_light, button_enough)

# colors_markup
colors_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
colors_markup.add(button_green, button_red, button_yellow, button_orange, button_lightblue, button_blue, button_purple)

# morph_markup
morph_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
morph_markup.add(button_open, button_grad, button_blackhat)

# morph_set_prof_markup
morph_set_prof_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
morph_set_prof_markup.add(button_morph_set_prof, button_enough)

# pixels filter amount of cut
pixel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
pixel_markup.add(button_2, button_4, button_8, button_16, button_32, button_enough)
