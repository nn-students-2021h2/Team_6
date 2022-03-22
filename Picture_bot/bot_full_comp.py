import os
from cv2 import imread, imwrite
from transliterate import translit
import logging
from aiogram import Bot, Dispatcher, executor
from requests import get
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from confidence_info.your_config import TOKEN
from confidence_info.your_dir import main_img_dir
import interface.all_states as FilterBotStates
from interface.markups import *
from exceptions import *
import Filters_Core as filters
from base import words_base

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

dp.middleware.setup(LoggingMiddleware())

url_img = "https://tortodelfeo.ru//wa-data/public/shop/products/88/27/2788/images/2648/2648.750.png"


# Вспомогательные функции
def get_user_images_dir(message):
    user_images_dir = os.path.join(main_img_dir, str(message.from_user.id))
    return user_images_dir


async def send_img_text_sticker(message, img_path, text, sticker, reply_markup=None):
    if img_path is not None:
        try:
            await bot.send_photo(message.chat.id, photo=open(img_path, 'rb'))
        except:
            try:
                await bot.send_photo(message.chat.id, get(img_path).content)
            except:
                await bot.send_message(message.chat.id, "Ошибка в получении пути к изображению")
    send = await bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=reply_markup)
    await bot.send_sticker(message.chat.id, open('Stickers/{}.webp'.format(sticker), 'rb'))
    return send


def create_save_path(message, images_type):
    src = os.path.join(get_user_images_dir(message),
                       images_type + "_" + translit(message.from_user.first_name, language_code='ru', reversed=True)
                       + ".jpg")
    return src


@dp.message_handler(commands="start", state="*")
async def start_message(message: types.Message):
    if not os.path.exists(get_user_images_dir(message)):
        await bot.send_message(message.chat.id, "О, да ты новенький")
        os.mkdir(get_user_images_dir(message))
    me = await bot.get_me()
    await FilterBotStates.StartManagment.ice_cream_not_done.set()
    await send_img_text_sticker(message, None, f"Добро пожаловать {message.from_user.first_name}!\n"
                                f"Я - <b>{me.first_name}</b>, Всемогущее Всесущее Зло!\
                                \n или просто бот созданный обработать твоё изображение",
                                "hello", 
                                reply_markup=start_markup)


@dp.message_handler(commands="help", state="*")
async def help_message(message: types.Message):
    await FilterBotStates.StartManagment.ice_cream_not_done.set()
    await send_img_text_sticker(message, None, words_base[1], "stupid", reply_markup=start_markup)


@dp.message_handler(lambda message: message.text == "🕵‍♂️Что ты умеешь?",
                    state=FilterBotStates.StartManagment.states)
async def help_message(message: types.Message):
    await FilterBotStates.StartManagment.ice_cream_not_done.set()
    await send_img_text_sticker(message, None, words_base[1], "stupid", reply_markup=start_markup)


@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку",
                    state=FilterBotStates.StartManagment.ice_cream_not_done)
async def wanted_icecream_first_time(message: types.Message):
    await FilterBotStates.StartManagment.ice_cream_done.set()
    await send_img_text_sticker(message, url_img, "Упс, я уже все съела", "hehe", start_markup)


@dp.message_handler(lambda message: message.text == "🍧 Хочу мороженку",
                    state=FilterBotStates.StartManagment.ice_cream_done)
async def wanted_icecream_other_time(message: types.Message):
    await send_img_text_sticker(message, url_img, "Думаешь что-то изменилось, пупсик?", "he", start_markup)


@dp.message_handler(lambda message: message.text == "🎨 Мне нужно обработать изображение",
                    state=[
                        FilterBotStates.StartManagment.ice_cream_done,
                        FilterBotStates.StartManagment.ice_cream_not_done,
                        FilterBotStates.ImageDownload.download_not_complete])
async def image_processing(message: types.Message):
    await FilterBotStates.ImageDownload.download_not_complete.set()
    await send_img_text_sticker(message, None, "Ну давай, кинь свою картинку", "giveme", types.ReplyKeyboardRemove())


# Не принимаем на обработку изображения, когда находимся в неправильном состоянии
@dp.message_handler(content_types=["photo"], state=FilterBotStates.StartManagment.states +
                                                  FilterBotStates.Filters.states +
                                                  FilterBotStates.Gamma_filter.states +
                                                  FilterBotStates.MorphManagment.states)
async def download_photo(message: types.Message):
    await send_img_text_sticker(message, None, "Ты слишком торопишься, я не такая", "nono", None)


# Начало обработки изображения
@dp.message_handler(content_types=["photo"], state=FilterBotStates.ImageDownload.states)
async def download_photo(message: types.Message):
    src = create_save_path(message, "source")
    try:
        await message.photo[-1].download(destination=src)
    except:
        await send_img_text_sticker(message, None, "У меня не получилось загрузить" + \
        "изображение, ты был слишком резок.. \n Попробуй другое 😟",
                                    "cry", None)
    else:
        await FilterBotStates.ImageDownload.download_done.set()
        filters_to_clear = [
            "negative", "gray", "mean_shift", "color_range", "pixel", "cartoon", "gamma", "open",
            "open", "grad", "sobel"]
        for clear_degit in filters_to_clear:
            if os.path.exists(create_save_path(message, clear_degit)):
                os.remove(create_save_path(message, clear_degit))
        await send_img_text_sticker(message, None, "Фото добавлено, братик, без слёз не взглянешь, дайка я поработаю",
                                    "omg", filters_markup)


# Обрабатываем сообщение "Исходник" и высылаем оригинал полученного ранее изображения
@dp.message_handler(lambda message: message.text == "Исходник",
                    state=FilterBotStates.ImageDownload.download_done)
async def get_source(message: types.Message):
    img_path = create_save_path(message, "source")
    await send_img_text_sticker(message, img_path, "С такого ракурса стало только хуже)", "haha", None)


# Обрабатываем сообщение "Негатив" и высылаем негативное изображение
@dp.message_handler(lambda message: message.text == "Негатив",
                    state=FilterBotStates.ImageDownload.download_done)
async def filter_negative(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "negative")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "negative")
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Negative_Filter(img)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "negative")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?",
                                        "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем сообщение "Черно-белый" и высылаем черно-белое изображение
@dp.message_handler(lambda message: message.text == "Черно-белый", state=FilterBotStates.ImageDownload.download_done)
async def filter_gray_scale(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "gray")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "gray")
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Gray_Filter(img)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "gray")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?",
                                        "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем запрос "Морфология"
@dp.message_handler(lambda message: message.text == "Морфология",
                    state=FilterBotStates.ImageDownload.download_done)
async def morph_choosing(message: types.Message):
    await FilterBotStates.Filters.morph_choosing_working.set()
    await send_img_text_sticker(message, None, "А какой именно тебя интересует?", "mayi", morph_markup)


# Останавливаем принятие запросов значений параметров для работы фильтров morph
@dp.message_handler(lambda message: message.text == "Перестань", state=FilterBotStates.MorphManagment.states)
async def reset(message: types.Message):
    await FilterBotStates.ImageDownload.download_done.set()
    await send_img_text_sticker(message, None, "Ладно, ладно. Что ты так завёлся", "evil", filters_markup)


# Обрабатываем выбор одного из семейства фильтров morph
@dp.message_handler(state=FilterBotStates.Filters.morph_choosing_working)
async def morph_settings_choosing(message: types.Message):
    if message.text in ["Открытие", "Черная шляпа", "Градиент"]:
        if message.text == "Открытие":
            await FilterBotStates.MorphManagment.open_working.set()
        elif message.text == "Градиент":
            await FilterBotStates.MorphManagment.grad_working.set()
        else:
            await FilterBotStates.MorphManagment.blackhat_working.set()
        await send_img_text_sticker(message, None, words_base[18], "mayi",
                                    set_prof_markup)
    else:
        await send_img_text_sticker(message, None, "Я такого не знаю, повтори-ка",
                                    "kus", morph_markup)


# Обрабатываем заданные параметры для работы фильтров morph
@dp.message_handler(state=FilterBotStates.MorphManagment.states)
async def morph_processing(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    current_state = str(current_state)
    if current_state == "MorphManagment:open_working":
        try:
            parametrs = filters.param(message.text, 'open')
        except:
            await send_img_text_sticker(message, None,
                                        "Ты неправильно меня понял, попробуй ещё раз", "kus",
                                        set_prof_markup)
        else:
            try:
                src_img_path = create_save_path(message, "source")
                img_path = create_save_path(message, "open")
                img = imread(src_img_path)
                if img is None:
                    raise ImreadError
                img_res = filters.Open_Filter(img, parametrs[0], parametrs[1])
                if not imwrite(img_path, img_res):
                    raise ImwriteError
                await FilterBotStates.MorphManagment.open_working.set()
                await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
            except ImreadError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
            except ImwriteError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
    elif current_state == "MorphManagment:grad_working":
        try:
            parametrs = filters.param(message.text, 'grad')
        except:
            await send_img_text_sticker(message, None,
                                        "Ты неправильно меня понял, попробуй ещё раз", "kus",
                                        set_prof_markup)
        else:
            try:
                src_img_path = create_save_path(message, "source")
                img_path = create_save_path(message, "grad")
                img = imread(src_img_path)
                if img is None:
                    raise ImreadError
                img_res = filters.Grad_Filter(img, parametrs[0], parametrs[1])
                if not imwrite(img_path, img_res):
                    raise ImwriteError
                await FilterBotStates.MorphManagment.grad_working.set()
                await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
            except ImreadError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
            except ImwriteError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)
    else:
        try:
            parametrs = filters.param(message.text, 'blackhat')
        except:
            await send_img_text_sticker(message, None,
                                        "Ты неправильно меня понял, попробуй ещё раз", "kus",
                                        set_prof_markup)
        else:
            try:
                src_img_path = create_save_path(message, "source")
                img_path = create_save_path(message, "blackhat")
                img = imread(src_img_path)
                if img is None:
                    raise ImreadError
                img_res = filters.Blackhat_Filter(img, parametrs[0], parametrs[1])
                if not imwrite(img_path, img_res):
                    raise ImwriteError
                await FilterBotStates.MorphManagment.blackhat_working.set()
                await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
            except ImreadError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
            except ImwriteError:
                await FilterBotStates.ImageDownload.download_done.set()
                await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем запрос "Мультиколизация"
@dp.message_handler(lambda message: message.text == "Мультиколизация",
                    state=FilterBotStates.ImageDownload.download_done)
async def filter_cartoon(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "cartoon")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "cartoon")
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Cartoon_Filter(img)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "cartoon")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?",
                                        "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем запрос "Цветовой диапазон"
@dp.message_handler(lambda message: message.text == "Цветовой диапазон",
                    state=FilterBotStates.ImageDownload.download_done)
async def colors(message: types.Message):
    await FilterBotStates.Filters.color_range_working.set()
    await send_img_text_sticker(message, None, "Введи один из цветов радуги, дорогуша", "mayi", colors_markup)


# Обрабатываем запрос с цветом на работу фильтра "Цветовой диапазон"
@dp.message_handler(state=FilterBotStates.Filters.color_range_working)
async def Color_Range(message: types.Message):
    try:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "color_range")
        img = imread(src_img_path)
        if img is None:
            raise ImreadError
        try:
            img_res = filters.Color_Range_Filter(img, message.text)
        except:
            await FilterBotStates.Filters.color_range_working.set()
            await send_img_text_sticker(message, None, "Сказала же, цвета радуги \n Каждый охотник желает знать..",
                                        "kus", colors_markup)
        if not imwrite(img_path, img_res):
            raise ImwriteError
        await FilterBotStates.ImageDownload.download_done.set()
        await send_img_text_sticker(message, img_path, "Ничего себе как я могу", "beautiful", filters_markup)
    except ImreadError:
        await FilterBotStates.ImageDownload.download_done.set()
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
    except ImwriteError:
        await FilterBotStates.ImageDownload.download_done.set()
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем запрос "Гамма Фильтр"
@dp.message_handler(lambda message: message.text == "Гамма Фильтр", state=FilterBotStates.ImageDownload.download_done)
async def filter_gamma(message: types.Message):
    await FilterBotStates.Gamma_filter.gamma_start.set()
    await send_img_text_sticker(message, None, "Введи свое значение гамма, сладкий", "giveme", baby_help_markup)


# Останавливаем принятие запросов значений параметров для работы фильтра gamma
@dp.message_handler(lambda message: message.text == "Перестань", state=FilterBotStates.Gamma_filter.states)
async def reset(message: types.Message):
    await FilterBotStates.ImageDownload.download_done.set()
    await send_img_text_sticker(message, None, "Ладно, ладно. Что ты так завёлся", "evil", filters_markup)


# Обрабатываем задачу параметров для gamma_filter
@dp.message_handler(state=[
                    FilterBotStates.Gamma_filter.gamma_start,
                    FilterBotStates.Gamma_filter.gamma_1])
async def Gamma_Function(message, state: FSMContext):
    current_state = await state.get_state()
    current_state = str(current_state)
    try:
        gamma_value = filters.Num((message.text + ' ')[: message.text.find(' ')])
        if gamma_value == 0.0:
            raise Zero_Error
    except Exception as e:
        if current_state == "Gamma_filter:gamma_start":
            await FilterBotStates.Gamma_filter.gamma_1.set()
            if str(type(e)) == "<class 'exceptions.Zero_Error'>":
                await send_img_text_sticker(message, None, "Ага, ноль, хорошо ты придумал..", "he", baby_help_markup)
            else:
                await send_img_text_sticker(message, None, "Гамма это просто число!", "kus", baby_help_markup)
        elif current_state == "Gamma_filter:gamma_1":
            await FilterBotStates.ImageDownload.download_done.set()
            await send_img_text_sticker(message, None, "Издеваешься, да?", "cry", filters_markup)
    else:
        try:
            if not os.path.exists(create_save_path(message, "gamma")):
                src_img_path = create_save_path(message, "source")
            else:
                src_img_path = create_save_path(message, "gamma")
            img_path = create_save_path(message, "gamma")
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Gamma_Filter(img, gamma_value)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await FilterBotStates.Gamma_filter.gamma_start.set()
            await send_img_text_sticker(message, img_path, "О да, я даже не ожидала, что так хорошо получится",
                                        "thatsgood",
                                        baby_help_markup)
        except ImreadError:
            await FilterBotStates.ImageDownload.download_done.set()
            await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        except ImwriteError:
            await FilterBotStates.ImageDownload.download_done.set()
            await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем запрос "Средний сдвиг"
@dp.message_handler(lambda message: message.text == "Средний сдвиг", state=FilterBotStates.ImageDownload.download_done)
async def filter_gamma(message: types.Message):
    await FilterBotStates.Filters.meanshift_working.set()
    await send_img_text_sticker(message, None, "Сколько раз хочешь хочешь, мм? Только чур не больше пяти",
                                "giveme", set_prof_markup)


# Останавливаем принятие запросов значений параметров для работы фильтров mean_shift
@dp.message_handler(lambda message: message.text == "Перестань", state=FilterBotStates.Filters.meanshift_working)
async def reset(message: types.Message):
    await FilterBotStates.ImageDownload.download_done.set()
    await send_img_text_sticker(message, None, "Ладно, ладно. Что ты так завёлся", "evil", filters_markup)


# Обрабатываем запрос "Средний сдвиг"
@dp.message_handler(state=FilterBotStates.Filters.meanshift_working)
async def filter_meanshift(message: types.Message):
    try:
        parametr = 0
        if message.text == "Поработай":
            parametr = 1
        else:
            parametr = int(message.text)
            if parametr == 0:
                raise Zero_Error
            if parametr > 5:
                raise Big_Error
            if parametr < 0:
                raise Minus_Error
    except Exception as e:
        if str(type(e)) == "<class 'exceptions.Zero_Error'>":
            await send_img_text_sticker(message, None, "Ага, ноль, хорошо ты придумал..", "he", set_prof_markup)
        elif str(type(e)) == "<class 'exceptions.Big_Error'>":
            await send_img_text_sticker(message, None, "Ого, какое больше число, а можно поменьше?", "kus",
                                        set_prof_markup)
        elif str(type(e)) == "<class 'exceptions.Minus_Error'>":
            await send_img_text_sticker(message, None, "Может ты еще и бесконечный двигатель изобретешь?", "kus",
                                        set_prof_markup)
        else:
            await send_img_text_sticker(message, None, "Я вроде число просила", "kus", set_prof_markup)
    else:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "mean_shift")
        try:
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Mean_Shift_Filter(img, parametr)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ах, как же я хорошо поработала", "wow", set_prof_markup)
        except ImreadError:
            await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        except ImwriteError:
            await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем сообщение "Пикселизация"
@dp.message_handler(lambda message: message.text == "Пикселизация",
                    state=FilterBotStates.ImageDownload.download_done)
async def params(message: types.Message):
    await FilterBotStates.Filters.pixel_working.set()
    await send_img_text_sticker(message, None, "Подрегулируй уровень пикселизации, введи число, нуу скажем, до 32",
                                "mayi", set_prof_markup)


# Останавливаем принятие запросов значений параметров для работы фильтров pixel
@dp.message_handler(lambda message: message.text == "Перестань", state=FilterBotStates.Filters.pixel_working)
async def reset(message: types.Message):
    await FilterBotStates.ImageDownload.download_done.set()
    await send_img_text_sticker(message, None, "Ладно, ладно. Что ты так завёлся", "evil", filters_markup)


# Обрабатываем задачу параметров для pixel_filter
@dp.message_handler(state=FilterBotStates.Filters.pixel_working)
async def filter_pixel(message: types.Message):
    try:
        parametr = 0
        if message.text == "Поработай":
            parametr = 2
        else:
            parametr = int(message.text)
            if parametr == 0:
                raise Zero_Error
            if parametr > 31:
                raise Big_Error
            if parametr < 0:
                raise Minus_Error
    except Exception as e:
        if str(type(e)) == "<class 'exceptions.Zero_Error'>":
            await send_img_text_sticker(message, None, "Ага, ноль, хорошо ты придумал..", "he", set_prof_markup)
        elif str(type(e)) == "<class 'exceptions.Big_Error'>":
            await send_img_text_sticker(message, None, "Ого, какое больше число, а можно поменьше?", "kus",
                                        set_prof_markup)
        elif str(type(e)) == "<class 'exceptions.Minus_Error'>":
            await send_img_text_sticker(message, None, "Может ты еще и бесконечный двигатель изобретешь?", "kus",
                                        set_prof_markup)
        else:
            await send_img_text_sticker(message, None, "Я вроде число просила", "kus", set_prof_markup)
    else:
        src_img_path = create_save_path(message, "source")
        img_path = create_save_path(message, "pixel")
        try:
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Pixel_Filter(img, parametr)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        except ImreadError:
            await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
        except ImwriteError:
            await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Обрабатываем сообщение "Выделить границы"
@dp.message_handler(lambda message: message.text == "Выделить границы", state=FilterBotStates.ImageDownload.download_done)
async def filter_sobel(message: types.Message):
    try:
        if not os.path.exists(create_save_path(message, "sobel")):
            src_img_path = create_save_path(message, "source")
            img_path = create_save_path(message, "sobel")
            img = imread(src_img_path)
            if img is None:
                raise ImreadError
            img_res = filters.Sobel_Filter(img)
            if not imwrite(img_path, img_res):
                raise ImwriteError
            await send_img_text_sticker(message, img_path, "Ммм, какая красивая фоточка", "looksgood", None)
        else:
            img_path = create_save_path(message, "sobel")
            await send_img_text_sticker(message, img_path, "Я что тебе робот туда сюда ее преобразовывать?",
                                        "iamnotarobot")
    except ImreadError:
        await send_img_text_sticker(message, None, "Файл не читается", "cry", filters_markup)
    except ImwriteError:
        await send_img_text_sticker(message, None, "Файл не записывается", "cry", filters_markup)


# Сбрасываем состояние до стартового
@dp.message_handler(lambda message: message.text == "Я устал",
                    state=FilterBotStates.ImageDownload.download_done)
async def image_processing(message: types.Message):
    await FilterBotStates.StartManagment.ice_cream_not_done.set()
    await send_img_text_sticker(message, None, "Бедненький, давай я тебя помогу тебе расслабиться ...", "relax",
                                start_markup)


# Обрабатвыем гифку и переотправляем
@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)


# Если ничего из вышеперечисленного не сработало
@dp.message_handler(state="*")
async def echo_message(message):
    await FilterBotStates.StartManagment.ice_cream_not_done.set()
    await send_img_text_sticker(message, None,
                                "Я не знаю что ответить 😢\n" + \
                                "Доступные команды: \n/start - полная перезагрузка \n" + \
                                "/help - информация о достурных фильтрах", "noanswer", start_markup)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
