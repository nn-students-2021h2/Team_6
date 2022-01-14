import os
import cv2
import numpy as np
from transliterate import translit
import asyncio
import logging
from aiogram import Bot, Dispatcher, executor
#from aiogram.utils.exceptions import BotBlocked
import aiogram.utils.markdown as fmt
from requests import get
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from confidence_info.your_config import TOKEN
from confidence_info.your_dir import main_img_dir
from interface.all_states import *
from interface.markups import *


bot = Bot(token = TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level = logging.INFO)

dp.middleware.setup(LoggingMiddleware())

tokens = {"negative": False, "gamma": False, "gray": False, "mean_shift": False,
        "color_range": False, "flag": 0}

# Вспомогательные функции
async def send_error_to_user(message, error_type):
    await send_img_text_sticker(message, None, error_type, "error", None)

async def send_img_text_sticker(message, img_path, text, sticker, reply_markup = None):
    if img_path is not None:
        try:
            await bot.send_photo(message.chat.id, photo=open(img_path, 'rb'))
        except:
            try:
                await bot.send_photo(message.chat.id, get(img_path).content)
            except:
                await send_error_to_user(message, "Ошибка в получении пути к изображению")
    send = await bot.send_message(message.chat.id, text, parse_mode='html', reply_markup = reply_markup)
    await bot.send_sticker(message.chat.id, open('Stickers/{}.webp'.format(sticker), 'rb'))
    return send

def create_save_path(message, images_type):
    user_images_dir = os.path.join(main_img_dir, translit(message.from_user.first_name, language_code='ru', reversed=True))
    src = os.path.join(user_images_dir, images_type + "_" + translit(message.from_user.first_name, language_code='ru', reversed=True) + ".jpg")
    return src


@dp.message_handler(commands = "start", state = "*")
async def start_message(message: types.Message):
    me = await bot.get_me()
    await send_img_text_sticker(message, None, f"{fmt.hide_link('https://www.youtube.com/watch?v=l6LC7B00fWw')}Добро пожаловать {message.from_user.first_name}!\n"
                                f"Я - <b>{me.first_name}</b>, Всемогущее Всесущее Зло!\n или просто бот созданный обработать", "hello", reply_markup = start_markup)
    await StartManagment.ice_crem_not_done.set()

@dp.message_handler(commands = "help", state = "*")
async def help_message(message: types.Message):
    me = await bot.get_me()
    await send_img_text_sticker(message, None, 
                                f"Давай-ка я подскажу тебе по поводу фильтров..\n"
                                f"<b>Негатив</b> - самый простой, значения каналов цвета меняются на противоположные\n"
                                f"<b>Гамма-фильтр</b> - чуть посложнее, в зависимости от коэффициента гамма меняется интенсивность(яркость) изображения\
                                посветлее, потемнее, всё такое..\n"
                                f"<b>Чёрно-белый</b> - ну туть всё понятно, находим интенсивность картинки и скалируем ее в оттенках от черного до белого цветов\n"
                                f"<b>Средний сдвиг</b> - скажу по-научному, он заменяет каждый пиксель средним значением пикселей в своей окрестности матрицы радиуса r 🧐\в общем гладит фото\n"
                                f"Ты еще не уснул? Оу, нет.. Ладно тогда продолжим\n"
                                f"<b>Цветовой диапазон</b> - да тут легко, эта штука выделяет диапазон цветов, который ты прикажешь\
                                и на картинке красит его в белый. Преобразовывем картинку в формат HSV (ну ты знаешь),\
                                создаём HSV массивы от минимума нашего оттенка цвета до максимума, ну а дальше всё понятно,\
                                это простейшая реализация, многого от нее не ожидай 🙄\n", "stupid", reply_markup = start_markup)
    await StartManagment.ice_crem_not_done.set()


#@dp.message_handler(commands="block", state = "*")
#async def cmd_block(message: types.Message):
#    await asyncio.sleep(10.0)  # Здоровый сон на 10 секунд
#    await message.reply("Вы заблокированы")

@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку", state = StartManagment.ice_crem_not_done)
async def wanted_icecrem_first_time(message: types.Message):
    await send_img_text_sticker(message, "https://sc01.alicdn.com/kf/UTB8CFH3C3QydeJk43PUq6AyQpXah/200128796/UTB8CFH3C3QydeJk43PUq6AyQpXah.jpg",
                                "Упс, я уже все съела", "hehe", start_markup)
    await send_img_text_sticker(message, None, f"{message.from_user.id}", "nono", None)
    await state.set_state(StartManagment.ice_crem_done)

@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку", state = StartManagment.ice_crem_done)
async def wanted_icecrem_other_time(message: types.Message):
    await send_img_text_sticker(message, "https://tortodelfeo.ru/wa-data/public/shop/products/88/27/2788/images/2648/2648.750.png",
                                "Думаешь что-то изменилось, пупсик ?", "he", start_markup)

@dp.message_handler(lambda message: message.text == "🎨 Мне нужно обработать изображение", state = StartManagment.states)
async def image_processing(message: types.Message):
    #await bot.send_message(message.chat.id, message.text, types.ReplyKeyboardRemove())
    await send_img_text_sticker(message, None, 'Тебе точно есть 18 ?', "18", markup_for_answer)
    await ImageDownload.download_not_complete.set()

@dp.message_handler(state = ImageDownload.download_not_complete)
async def echo_message(message: types.Message):
    await send_img_text_sticker(message, None, "Чего я там не видела, ответь на вопрос, малыш, тебе есть 18 ?",
                                 "be", markup_for_answer)

@dp.callback_query_handler(text = "years_old_18", state = "*")
async def send_random_value(call: types.CallbackQuery):
    await send_img_text_sticker(call.message, None, "Кидай свою картинку...", "giveaphoto", types.ReplyKeyboardRemove())
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Тебе точно есть 18 ?',
                reply_markup=None)
    await ImageDownload.prepare_downloading.set()
    asyncio.sleep(4)
    await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                              text = "Я уже заждалась твоего изображения")

@dp.callback_query_handler(text = "years_old_not_18", state = "*")
async def send_random_value(call: types.CallbackQuery):
    await send_img_text_sticker(call.message, None, "Ну ничего, со всеми бывало, загружай изображение!", "giveaphoto", types.ReplyKeyboardRemove())
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Тебе точно есть 18 ?',
                reply_markup=None)
    await ImageDownload.prepare_downloading.set()
    asyncio.sleep(4)
    await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                              text = "Я уже заждалась твоего изображения")

@dp.message_handler(content_types = ["photo"], state = StartManagment.states)
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "Ты слишком торопишься, я не такая", "nono", None)

@dp.message_handler(content_types = ["photo"], state = ImageDownload.download_done)
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "Я не обрабатываю случаное изображение, зайка", "dontrush", start_markup)

@dp.message_handler(content_types = ["photo"], state = ImageDownload.download_not_complete)
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "Ты слишком торопишься, я не такая", "nono", None)

@dp.message_handler(content_types = ["photo"], state = Filters.states)
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "И зачем мне это сейчас ?", "stupid", None)

@dp.message_handler(content_types = ["photo"], state = ImageDownload.prepare_downloading)
async def download_photo(message: types.Message):
    try:
        user_images_dir = os.path.join(main_img_dir, translit(message.from_user.first_name, language_code='ru', reversed=True))
        #user_images_dir = os.path.join(main_img_dir, str(message.from_user.id))
        src = create_save_path(message, "source")
        try:
            await message.photo[-1].download(destination = src)
        except:
            os.mkdir(user_images_dir)
            await message.photo[-1].download(destination = src)
        await send_img_text_sticker(message, None, "Фото добавлено, братик, без слёз не взглянешь, дайка я поработаю", "omg", filters_markup)
        await ImageDownload.download_done.set()
        tokens["negative"] = False
        tokens["mean_shift"] = False
        tokens["gray"] = False
        tokens["gamma"] = False
        tokens["color_range"] = False
    except:
        await send_error_to_user(message, "У меня не получилось загрузить изображение, ты был слишком резок.. \n Попробуй другое 😟")

@dp.message_handler(lambda message: message.text == "Исходник", state = ImageDownload.download_done)
async def get_source(message: types.Message):
    try:
        img_path = create_save_path(message, "source")
        await send_img_text_sticker(message, img_path, "С такого ракурса стало только хуже XD", "haha", None)
    except:
        await send_error_to_user(message, "Ой, а я не видела твоих фоточек еще...")

@dp.message_handler(lambda message: message.text == "Негатив", state = ImageDownload.download_done)
async def filter_negative(message: types.Message):
    if (tokens["negative"] == False):
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "negative")
        img = cv2.imread(src_img_path)
        img_not = cv2.bitwise_not(img)
        cv2.imwrite(img_path, img_not)
        await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        tokens["negative"] = True
    else:
        img_path = create_save_path(message, "negative")
        await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?", "iamnotarobot")

@dp.message_handler(lambda message: message.text == "Черно-белый", state = ImageDownload.download_done)
async def filter_gray_scale(message: types.Message):
    if tokens.get('gray') == False:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "gray")
        img = cv2.imread(src_img_path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(img_path, img_gray)
        await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        tokens['gray'] = True
    else:
        img_path = create_save_path(message, "gray")
        await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?", "iamnotarobot")

@dp.message_handler(lambda message: message.text == "Цветовой диапазон", state = ImageDownload.download_done)
async def colors(message: types.Message):
    await send_img_text_sticker(message, None, "Введи один из цветов радуги, дорогуша","mayi", colors_markup)
    await Filters.color_range_working.set()

@dp.message_handler(state = Filters.color_range_working)
async def Color_Range(message: types.Message):
    # try:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "color_range")
        img = cv2.imread(src_img_path)
        img = cv2.bilateralFilter(img,9,75,75)
        if message.text == 'Зелёный' or message.text == 'зелёный' or message.text == 'зеленый' \
                                        or message.text == 'Зеленый' or message.text == 'green':
            hsv_min = np.array((36, 25, 25), np.uint8)
            hsv_max = np.array((85, 255, 255), np.uint8)
        elif message.text == 'Красный' or message.text == 'красный' or message.text == 'red':
            hsv_min = np.array((0, 25, 25), np.uint8)
            hsv_max = np.array((15, 255, 255), np.uint8)
        elif message.text == 'Оранжевый' or message.text == 'оранжевый' or message.text == 'orange':
            hsv_min = np.array((13, 25, 25), np.uint8)
            hsv_max = np.array((23, 255, 255), np.uint8)
        elif message.text == 'Жёлтый' or message.text == 'жёлтый' or message.text == 'желтый' \
                                     or message.text == 'Желтый' or message.text == 'yellow':
            hsv_min = np.array((20, 25, 25), np.uint8)
            hsv_max = np.array((40, 255, 255), np.uint8)
        elif message.text == 'Голубой' or message.text == 'голубой' or message.text == 'blue':
            hsv_min = np.array((83, 25, 25), np.uint8)
            hsv_max = np.array((103, 255, 255), np.uint8)
        elif message.text == 'Синий' or message.text == 'синий' or message.text == 'light blue':
            hsv_min = np.array((103, 25, 25), np.uint8)
            hsv_max = np.array((133, 255, 255), np.uint8)
        elif message.text == 'Фиолетовый' or message.text == 'фиолетовый' or message.text == 'purple':
            hsv_min = np.array((135, 0, 0), np.uint8)
            hsv_max = np.array((155, 255, 255), np.uint8)
        else:
            await send_img_text_sticker(message, None, "Сказала же, цвета радуги \n Каждый охотник желает знать..", "kus", None)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.inRange(hsv, hsv_min, hsv_max)
        cv2.imwrite(img_path, img_hsv)
        tokens['color_range'] = True
        await send_img_text_sticker(message, img_path, "Ничего себе как я могу", "beautiful", filters_markup)
        await ImageDownload.download_done.set()
    # except:
    #     await send_img_text_sticker(message, None, "Что-то пошло не так, прости..", "cry", filters_markup)
    #     ImageDownload.download_done.set()

@dp.message_handler(lambda message: message.text == "Гамма Фильтр", state = ImageDownload.download_done)
async def filter_gamma(message: types.Message):
    tokens["flag"] = 0
    if tokens["gamma"] == False:
        await send_img_text_sticker(message, None, "Тебе подсказать значение гамма, милашка?","mayi", baby_help_markup)
        await Filters.gamma_working.set()
    else:
        await send_img_text_sticker(message, None, "Введи свое значение гамма, сладкий", "giveme", baby_enough_markup)
        await Filters.gamma_working.set()

def adjust_gamma(image, gamma = 1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

@dp.message_handler(state = Filters.gamma_working)
async def Gamma_Function(message):
    if message.text == '0.5 Немного затемнить':
        if tokens.get('gamma') == False:
            src_img_path = create_save_path(message, "source")
        else:
            src_img_path = create_save_path(message, "gamma")
        img_path = create_save_path(message, "gamma")
        img = cv2.imread(src_img_path)
        img_gamma = adjust_gamma(img, 0.5)
        img = cv2.imwrite(img_path, img_gamma)
        await send_img_text_sticker(message, img_path, "Ух, как же красиво стало", "beautiful", filters_markup)
        tokens['gamma'] = True
        await ImageDownload.download_done.set()
    elif message.text == '1.5 Немного осветлить':
        if tokens.get('gamma') == False:
            src_img_path = create_save_path(message, "source")
        else:
            src_img_path = create_save_path(message, "gamma")
        img_path = create_save_path(message, "gamma")
        img = cv2.imread(src_img_path)
        img_gamma = adjust_gamma(img, 1.5)
        img = cv2.imwrite(img_path, img_gamma)
        await send_img_text_sticker(message, img_path, "Намного лучше, чем было 😉", "nowbetter", filters_markup)
        tokens['gamma'] = True
        await ImageDownload.download_done.set()
    elif message.text == 'Перестань (reset brightnes)':
        await send_img_text_sticker(message, None, "Ладно, ладно", "evil", filters_markup)
        tokens['gamma'] = False
        await ImageDownload.download_done.set()
    else:
        try:
            gamma = (float)(message.text)
        except:
            tokens["flag"] += 1
            if tokens["flag"] == 1:
                await send_img_text_sticker(message, None, "Гамма это просто число!", "kus", baby_help_markup)
            if tokens["flag"] == 2:
                await send_img_text_sticker(message, None, "Издеваешься, да?", "cry", filters_markup)
                await ImageDownload.download_done.set()
        if tokens["flag"] == 0:
            if tokens.get('gamma') == False:
                src_img_path = create_save_path(message, "source")
            else:
                src_img_path = create_save_path(message, "gamma")
            img_path = create_save_path(message, "gamma")
            img = cv2.imread(src_img_path)
            img_gamma = adjust_gamma(img, gamma)
            img = cv2.imwrite(img_path, img_gamma)
            await send_img_text_sticker(message, img_path, "О да, я даже не ожидала, что так хорошо получится", "thatsgood", filters_markup)
            await ImageDownload.download_done.set()

@dp.message_handler(lambda message: message.text == "Средний сдвиг", state = ImageDownload.download_done)
async def filter_meanshift(message: types.Message):
    if tokens.get('mean_shift') == False:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "mean_shift")
        img = cv2.imread(src_img_path)
        image_shifted = cv2.pyrMeanShiftFiltering(img, 10, 25)
        cv2.imwrite(img_path, image_shifted)
        await send_img_text_sticker(message, img_path, "Ах, как же я хорошо поработала", "wow", None)
        tokens['mean_shift'] = True
    else:
        img_path = create_save_path(message, "mean_shift")
        await send_img_text_sticker(message, img_path, "Ты уже использовал этот фильтр, имей совесть! Я тут не без дела сижу ...", "tired")

@dp.message_handler(lambda message: message.text == "Я устал", state = ImageDownload.download_done)
async def image_processing(message: types.Message):
    await send_img_text_sticker(message, None, "Бедненький, давай я тебя помогу тебе расслабиться ...", "relax", start_markup)
    await StartManagment.ice_crem_not_done.set()

@dp.message_handler(content_types = [types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)

#@dp.errors_handler(exception=BotBlocked)
#async def error_bot_blocked(update: types.Update, exception: BotBlocked):
#    # Update: объект события от Telegram. Exception: объект исключения
#    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
#    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

#    # Такой хэндлер должен всегда возвращать True,
#    # если дальнейшая обработка не требуется.
#    return True

#@dp.message_handler(commands = "answer")
#async def cmd_answer(message: types.Message):
#    await message.answer("Это простой ответ")

#@dp.message_handler(commands="reply")
#async def cmd_reply(message: types.Message):
#    await message.reply('Это ответ с "ответом"')

@dp.message_handler(state = "*")
async def echo_message(message):
    await send_img_text_sticker(message, None,
    f"Я не знаю что ответить 😢\n"
    f"Доступные команды: \n/start - полная перезагрузка \n"
    f"/help - информация о достурных фильтрах", "noanswer", start_markup)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)