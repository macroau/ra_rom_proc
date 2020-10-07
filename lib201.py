# -*- coding: utf-8 -*-
# cython: language_level=3

from PIL import Image

def pil_conv_img(src, dst):
    im = Image.open(src)
    im.save(dst)

#EOF