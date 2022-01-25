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
import interface.all_states as FilterBotStates
from interface.markups import *
from exceptions import *

bot = Bot(token = TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level = logging.INFO)

dp.middleware.setup(LoggingMiddleware())

tokens = {"flag": 0}
colors_dect = {
    'Зелёный': {'min': 30, 'max': 85}, 'Зеленый': {'min': 30, 'max': 85},
    'Красный': {'min': 160, 'max': 180},
    'Оранжевый': {'min': 10, 'max': 25},
    'Жёлтый': {'min': 20, 'max': 40}, 'Желтый': {'min': 20, 'max': 40},
    'Голубой': {'min': 80, 'max': 110},
    'Синий': {'min': 100, 'max': 135},
    'Фиолетовый': {'min': 135, 'max': 160}
    }
# Вспомогательные функции
def get_user_images_dir(message):
    user_images_dir = os.path.join(main_img_dir, str(message.from_user.id))
    return user_images_dir

async def send_img_text_sticker(message, img_path, text, sticker, reply_markup = None):
    if img_path is not None:
        try:
            await bot.send_photo(message.chat.id, photo=open(img_path, 'rb'))
        except:
            try:
                await bot.send_photo(message.chat.id, get(img_path).content)
            except:
                await bot.send_message(message.chat.id, "Ошибка в получении пути к изображению")
    send = await bot.send_message(message.chat.id, text, parse_mode='html', reply_markup = reply_markup)
    await bot.send_sticker(message.chat.id, open('Stickers/{}.webp'.format(sticker), 'rb'))
    return send

def create_save_path(message, images_type):
    src = os.path.join(get_user_images_dir(message),
                      images_type + "_" + translit(message.from_user.first_name, language_code='ru', reversed=True) + ".jpg")
    return src

def adjust_gamma(image, gamma = 1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

@dp.message_handler(commands = "start", state = "*")
async def start_message(message: types.Message):
    if not os.path.exists(get_user_images_dir(message)):
        await bot.send_message(message.chat.id, "О, да ты новенький")
        os.mkdir(get_user_images_dir(message))
    me = await bot.get_me()
    await send_img_text_sticker(message, None, f"Добро пожаловать {message.from_user.first_name}!\n"
                                f"Я - <b>{me.first_name}</b>, Всемогущее Всесущее Зло!\n или просто бот созданный обработать твоё изображение",
                                "hello", 
                                reply_markup = start_markup)
    await FilterBotStates.StartManagment.ice_cream_not_done.set()

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
    await StartManagment.ice_cream_not_done.set()

@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку", state = FilterBotStates.StartManagment.ice_cream_not_done)
async def wanted_icecream_first_time(message: types.Message):
    await send_img_text_sticker(message, "https://sc01.alicdn.com/kf/UTB8CFH3C3QydeJk43PUq6AyQpXah/200128796/UTB8CFH3C3QydeJk43PUq6AyQpXah.jpg",
                                "Упс, я уже все съела", "hehe", start_markup)
    await send_img_text_sticker(message, None, f"{message.from_user.id}", "nono", None)
    await FilterBotStates.StartManagment.ice_cream_done.set()

@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку", state = FilterBotStates.StartManagment.ice_cream_done)
async def wanted_icecream_other_time(message: types.Message):
    await send_img_text_sticker(message, "https://tortodelfeo.ru/wa-data/public/shop/products/88/27/2788/images/2648/2648.750.png",
                                "Думаешь что-то изменилось, пупсик ?", "he", start_markup)

@dp.message_handler(lambda message: message.text == "🎨 Мне нужно обработать изображение",
                    state = FilterBotStates.StartManagment.states)
async def image_processing(message: types.Message):
    await send_img_text_sticker(message, None,
                            "Ну давай, кинь свою картинку", "giveme", filters_markup)
    await FilterBotStates.ImageDownload.download_not_complete.set()

#Не принимаем на обработку изображения, когда находимся в неправильном состоянии
@dp.message_handler(content_types = ["photo"], state = [FilterBotStates.StartManagment.ice_cream_not_done,
                                                        FilterBotStates.StartManagment.ice_cream_done, 
                                                        FilterBotStates.Filters.color_range_working,
                                                        FilterBotStates.Filters.gamma_working])
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "Ты слишком торопишься, я не такая", "nono", None)

#Начало обработки изображения
@dp.message_handler(content_types = ["photo"], state = FilterBotStates.ImageDownload.states)
async def download_photo(message: types.Message):
    src = create_save_path(message, "source")
    try:
        await message.photo[-1].download(destination = src)
    except:
        await send_img_text_sticker(message, None,
                                    "У меня не получилось загрузить изображение, ты был слишком резок.. \n Попробуй другое 😟", "cry", None)
    else:
        filters_to_clear = ["negative", "gray", "mean_shift", "pixel"]
        for filter in filters_to_clear:
            if os.path.exists(create_save_path(message, filter)):
                os.remove(create_save_path(message, filter))
        await send_img_text_sticker(message, None, "Фото добавлено, братик, без слёз не взглянешь, дайка я поработаю", "omg", filters_markup)
        await FilterBotStates.ImageDownload.download_done.set()

# Обрабатываем сообщение "Исходник" и высылаем оригинал полученного ранее изображения
@dp.message_handler(lambda message: message.text == "Исходник", state = FilterBotStates.ImageDownload.download_done)
async def get_source(message: types.Message):
    img_path = create_save_path(message, "source")
    await send_img_text_sticker(message, img_path, "С такого ракурса стало только хуже XD", "haha", None)

# Обрабатываем сообщение "Негатив" и высылаем негативное изображение
@dp.message_handler(lambda message: message.text == "Негатив", state = FilterBotStates.ImageDownload.download_done)
async def filter_negative(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "negative")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "negative")
            img = cv2.imread(src_img_path)
            if img is None:
                raise ImreadError
            img_not = cv2.bitwise_not(img)
            if cv2.imwrite(img_path, img_not) == False:
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "negative")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?", "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        FilterBotStates.ImageDownload.download_done.set()
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
        FilterBotStates.ImageDownload.download_done.set()

# Обрабатываем сообщение "Черно-белый" и высылаем черно-белое изображение
@dp.message_handler(lambda message: message.text == "Черно-белый", state = FilterBotStates.ImageDownload.download_done)
async def filter_gray_scale(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "gray")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "gray")
            img = cv2.imread(src_img_path)
            if img is None:
                raise ImreadError
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if cv2.imwrite(img_path, img_gray) == False:
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "gray")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?", "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        FilterBotStates.ImageDownload.download_done.set()
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
        FilterBotStates.ImageDownload.download_done.set()

@dp.message_handler(lambda message: message.text == "Цветовой диапазон", state = FilterBotStates.ImageDownload.download_done)
async def colors(message: types.Message):
    await send_img_text_sticker(message, None, "Введи один из цветов радуги, дорогуша","mayi", colors_markup)
    await FilterBotStates.Filters.color_range_working.set()

@dp.message_handler(state = FilterBotStates.Filters.color_range_working)
async def Color_Range(message: types.Message):
    try:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "color_range")
        img = cv2.imread(src_img_path)
        if img is None:
            raise ImreadError
        #img = cv2.bilateralFilter(img,9,151,151)
        for i in range(2):
            img = cv2.bilateralFilter(img,9,75,75)
        try:
            hsv_min = np.array((colors_dect[message.text]['min'], 100, 20), np.uint8)
            hsv_max = np.array((colors_dect[message.text]['max'], 255, 255), np.uint8)
        except:
            await send_img_text_sticker(message, None, "Сказала же, цвета радуги \n Каждый охотник желает знать..", "kus", colors_markup)
            await FilterBotStates.Filters.color_range_working.set()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv = cv2.inRange(hsv, hsv_min, hsv_max)
        if cv2.imwrite(img_path, img_hsv) == False:
            raise ImwriteError
        await send_img_text_sticker(message, img_path, "Ничего себе как я могу", "beautiful", filters_markup)
        await FilterBotStates.ImageDownload.download_done.set()
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        await FilterBotStates.ImageDownload.download_done.set()
    #except ColorEnterError:
    #    await send_img_text_sticker(message, None, "Сказала же, цвета радуги \n Каждый охотник желает знать..", "kus", colors_markup)
    #    Filters.color_range_working.set()
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
        await FilterBotStates.ImageDownload.download_done.set()

@dp.message_handler(lambda message: message.text == "Гамма Фильтр", state = FilterBotStates.ImageDownload.download_done)
async def filter_gamma(message: types.Message):
    tokens["flag"] = 0
    if not os.path.exists(create_save_path(message, "gamma")):
        await send_img_text_sticker(message, None, "Тебе подсказать значение гамма, милашка?","mayi", baby_help_markup)
        await FilterBotStates.Filters.gamma_working.set()
    else:
        await send_img_text_sticker(message, None, "Введи свое значение гамма, сладкий", "giveme", baby_enough_markup)
        await FilterBotStates.Filters.gamma_working.set()

@dp.message_handler(state = FilterBotStates.Filters.gamma_working)
async def Gamma_Function(message):
    if message.text == 'Перестань (reset brightnes)':
        await send_img_text_sticker(message, None, "Ладно, ладно", "evil", filters_markup)
        await FilterBotStates.ImageDownload.download_done.set()
    else:
        try:
            gamma = message.text[: message.text.find(" ")]
            gamma = float(gamma)
        except: # какая ошибка
            tokens["flag"] += 1
            if tokens["flag"] == 1:
                await send_img_text_sticker(message, None, "Гамма это просто число!", "kus", baby_help_markup)
            if tokens["flag"] == 2:
                tokens["flag"] = 1
                await send_img_text_sticker(message, None, "Издеваешься, да?", "cry", baby_help_markup)
                await FilterBotStates.ImageDownload.download_done.set()
        else:
            tokens['flag'] = 0

        if tokens["flag"] == 0:
            try:
                if not os.path.exists(create_save_path(message, "gamma")):
                    src_img_path = create_save_path(message, "source")
                else:
                    src_img_path = create_save_path(message, "gamma")
                img_path = create_save_path(message, "gamma")
                img = cv2.imread(src_img_path)
                if img is None:
                    raise ImreadError
                img_gamma = adjust_gamma(img, gamma)
                if cv2.imwrite(img_path, img_gamma) == False:
                    raise ImwriteError
                await send_img_text_sticker(message, img_path, "О да, я даже не ожидала, что так хорошо получится", "thatsgood", filters_markup)
                await FilterBotStates.ImageDownload.download_done.set()
            except ImreadError:
                await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
                await FilterBotStates.ImageDownload.download_done.set()
            except ImwriteError:
                await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
                await FilterBotStates.ImageDownload.download_done.set()

@dp.message_handler(lambda message: message.text == "Средний сдвиг", state = FilterBotStates.ImageDownload.download_done)
async def filter_meanshift(message: types.Message):
        if not os.path.exists(create_save_path(message, "mean_shift")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "mean_shift")
            try:
                img = cv2.imread(src_img_path)
                if img is None:
                    raise ImreadError
                image_shifted = cv2.pyrMeanShiftFiltering(img, 15, 50, 1)
                if cv2.imwrite(img_path, image_shifted) == False:
                    raise ImwriteError
                await send_img_text_sticker(message, img_path, "Ах, как же я хорошо поработала", "wow", None)
            except ImreadError:
                await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
            except ImwriteError:
                await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
        else:
            img_path = create_save_path(message, "mean_shift")
            await send_img_text_sticker(message, img_path, "Ты уже использовал этот фильтр, имей совесть! Я тут не без дела сижу ...", "tired")

@dp.message_handler(lambda message: message.text == "Пикселизация", state = FilterBotStates.ImageDownload.download_done)
async def filter_pixel(message: types.Message):
    if not os.path.exists(create_save_path(message, "pixel")):
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "pixel")
        try:
            img = cv2.imread(src_img_path)
            if img is None:
                raise ImreadError
            orig_height, orig_width = img.shape[:2]
            small_height, small_width = orig_height // 4, orig_width // 4
            img_resized = cv2.resize(img, (small_width, small_height), interpolation = cv2.INTER_LINEAR)

            data = img_resized.reshape((-1,3))
            data = np.float32(data)
            criteria = (cv2.TERM_CRITERIA_EPS +
                        cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv2.KMEANS_RANDOM_CENTERS
            compactness, labels, centers = cv2.kmeans(data, 20, None, criteria, 10, flags)
            centers = np.uint8(centers)
            res = centers[labels.flatten()]
            img_resized = res.reshape((img_resized.shape))

            img_resized = cv2.resize(img_resized, (orig_width, orig_height), interpolation = cv2.INTER_NEAREST)
            if cv2.imwrite(img_path, img_resized) == False:
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        except ImreadError:
            await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        except ImwriteError:
            await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
    else:
        img_path = create_save_path(message, "pixel")
        await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?", "iamnotarobot")

@dp.message_handler(lambda message: message.text == "Я устал", state = FilterBotStates.ImageDownload.download_done)
async def image_processing(message: types.Message):
    await send_img_text_sticker(message, None, "Бедненький, давай я тебя помогу тебе расслабиться ...", "relax", start_markup)
    await FilterBotStates.StartManagment.ice_cream_not_done.set()

@dp.message_handler(content_types = [types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)

@dp.message_handler(state = "*")
async def echo_message(message):
    await send_img_text_sticker(message, None,
    f"Я не знаю что ответить 😢\n"
    f"Доступные команды: \n/start - полная перезагрузка \n"
    f"/help - информация о достурных фильтрах", "noanswer", start_markup)

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
