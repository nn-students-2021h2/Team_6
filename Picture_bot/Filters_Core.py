import cv2
import numpy as np
import Cartoon_Neuro as CN
colors_dict = {
    'Зелёный': {'min': 30, 'max': 85}, 'Зеленый': {'min': 30, 'max': 85},
    'Красный': {'min': 160, 'max': 180},
    'Оранжевый': {'min': 10, 'max': 25},
    'Жёлтый': {'min': 20, 'max': 40}, 'Желтый': {'min': 20, 'max': 40},
    'Голубой': {'min': 80, 'max': 110},
    'Синий': {'min': 100, 'max': 135},
    'Фиолетовый': {'min': 135, 'max': 160}
    }


def Negative_Filter(img):
    return cv2.bitwise_not(img)


def Gray_Filter(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def Mean_Shift_Filter(img):
    return cv2.pyrMeanShiftFiltering(img, 15, 50, None, 1)


def Color_Range_Filter(img, color: str):
    # img = cv2.bilateralFilter(img,9,151,151)
    for i in range(2):
        img = cv2.bilateralFilter(img, 9, 75, 75)
    hsv_min = np.array((colors_dict[color]['min'], 100, 20), np.uint8)
    hsv_max = np.array((colors_dict[color]['max'], 255, 255), np.uint8)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_res = cv2.inRange(hsv, hsv_min, hsv_max)
    return img_res


def Gamma_Num(num):
    return float(num)


def param(message, type):
    if "Поработай" in message:
        if type == 'blur':
            return [9, 3]
        elif type == 'border':
            return [7, 2]
        else:
            return [7, 20]

    parametrs = message.split(' ')
    if len(parametrs) != 2:
        raise
    parametrs = list(map(int, parametrs))
    if parametrs[0] < 1 or parametrs[1] < 1 or parametrs[0] > 200 or parametrs[1] > 200 or parametrs[0] % 2 == 0:
        raise
    return parametrs


def cut_param(message):
    cut = int(message)
    if cut == 2 or cut == 4 or cut == 8 or cut == 16 or cut == 32:
        return cut
    else:
        raise


def Gamma_Filter(img, gamma: float):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(img, table)


def Pixel_Filter(img, cut=4):
    orig_height, orig_width = img.shape[:2]
    small_height, small_width = orig_height // cut, orig_width // cut
    img_res = cv2.resize(img, (small_width, small_height), interpolation=cv2.INTER_LINEAR)
    data = img_res.reshape((-1, 3))
    data = np.float32(data)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 20, None, criteria, 10, flags)
    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    img_res = res.reshape(img_res.shape)
    img_res = cv2.resize(img_res, (orig_width, orig_height), interpolation=cv2.INTER_NEAREST)
    return img_res


def Morph_Filter(img, mode, arr_size):
    # define MORPH_OPEN         2
    # define MORPH_CLOSE        3
    # define MORPH_GRADIENT     4
    # define MORPH_TOPHAT       5
    # define MORPH_BLACKHAT     6

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (arr_size, arr_size))
    img_res = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel, iterations=1)
    # img_res = cv2.morphologyEx(img_res, cv2.MORPH_GRADIENT, kernel3, iterations=1)
    img_res = cv2.morphologyEx(img_res, cv2.MORPH_TOPHAT, kernel, iterations=10)
    # img_res = cv2.cvtColor(img_res, cv2.COLOR_BGR2GRAY)
    # img_res = cv2.morphologyEx(img_res, cv2.MORPH_OPEN, kernel3, iterations=1)
    return img_res


def Grad_Filter(img, arr_size, degree):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (arr_size, arr_size))
    img_res = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel, iterations=degree)
    img_res = Negative_Filter(img_res)
    return img_res


def Sobel_Filter(img):
    x = cv2.Sobel(img, cv2.CV_16S, 1, 0)
    y = cv2.Sobel(img, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(x)  # Перенести обратно на uint8
    absY = cv2.convertScaleAbs(y)  # Перенести обратно на uint8
    img_res = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    img_res = cv2.cvtColor(img_res, cv2.COLOR_BGR2GRAY)
    return img_res


def Blackhat_Filter(img, arr_size, degree):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (arr_size, arr_size))
    img_res = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel, iterations=degree)

    return img_res


def Open_Filter(img, arr_size, degree):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (arr_size, arr_size))
    img_res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=degree)

    return img_res


def Cartoon_Filter(img, batch_size=4):
    return CN.main(img, batch_size, 'cpu')


if __name__ == '__main__':
    img = cv2.imread('C:/PNGLIVE/test4.jpg')
    cv2.imshow('image1', img)
    cv2.imshow('image2', Border_Filter(img, 7, 2))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

