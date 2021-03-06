"""numpy util

* np_img(single numpy image ) is numpy array with shape WHC
* np_imgs(multiple numpy images) is numpy array with shape NWHC
"""
from PIL import Image
from skimage import color, io
import math
import numpy as np


def np_img_float32_to_uint8(np_img):
    """type cast numpy image from float to uint8

    :type np_img: numpy.array
    :param np_img: numpy array image

    :return: uint8 type numpy image(HWC shape)
    """
    return np.uint8(np_img * 255)


def np_img_uint8_to_float32(np_img):
    """type cast numpy image from uint8 to float32

    :type np_img: numpy.array
    :param np_img: numpy array image

    :return: float32 type numpy image(HWC shape)
    """
    return np.float32(np_img) / 255.0


def np_img_rgb_to_gray(np_img):
    """convert numpy image from rgb to gary scale

    :type np_img: numpy.array
    :param np_img: numpy array image

    :return: gray scale numpy image(HWC shape)
    """
    return np.uint8(color.rgb2gray(np_img) * 255)


def np_img_gray_to_rgb(np_img):
    """convert numpy image from gray scale to rgb

    :type np_img: numpy.array
    :param np_img: numpy array image

    :return: rgb numpy image(HWC shape)
    """
    return color.gray2rgb(np_img)


def np_img_to_PIL_img(np_img):
    """convert numpy image to PIL Image

    :type np_img: numpy.array
    :param np_img: numpy image

    :return: PIL Image
    """
    return Image.fromarray(np_img)


def np_img_load_file(path):
    """load numpy image from file

    :type path: str
    :param path:path to load image file

    :return: numpy image(HWC shape)
    """
    return io.imread(path)


def np_img_to_tile(np_imgs, column_size=10):
    """convert multiple numpy images to one grid tile image

    :type np_imgs: numpy.array
    :type column_size: int
    :param np_imgs: numpy images
    numpy image shape expect NHWC
    :param column_size: column size of grid tile image

    :return: gird tiled numpy image(HWC shape)
    """
    n, h, w, c = np_imgs.shape
    row_size = int(math.ceil(float(np_imgs.shape[0]) / float(column_size)))
    tile_width = w * column_size
    tile_height = h * row_size

    img_idx = 0
    # HWC format
    tile = np.ones((tile_height, tile_width, 3), dtype=np.uint8)
    for y in range(0, tile_height, h):
        for x in range(0, tile_width, w):
            if img_idx >= n:
                break

            tile[y:y + h, x:x + w, :] = np_imgs[img_idx]
            img_idx += 1

        if img_idx >= n:
            break

    return tile


def np_imgs_NCWH_to_NHWC(imgs):
    """convert numpy images shape NCWH to NHWC

    :type imgs: numpy.array
    :param imgs: numpy images

    :return: numpy images(NHWC shape)
    """
    return np.transpose(imgs, [0, 2, 3, 1])


def np_index_to_onehot(x, n=None, dtype=float):
    """1-hot encode x with the max value n (computed from data if n is None).

    :param x: numpy array
    :param n: max value
    :param dtype:data type

    :return: numpy array
    """
    x = np.asarray(x)
    n = np.max(x) + 1 if n is None else n
    return np.eye(n, dtype=dtype)[x]
