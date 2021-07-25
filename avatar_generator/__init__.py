#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

"""
    Generates default avatars from a given fullname (such as username).

    Usage:

    >>> from avatar_generator import Avatar
    >>> photo = Avatar.generate(128, "example@sysnove.fr", "PNG")
"""

import os
from random import randint, seed
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

__all__ = ['Avatar']


class Avatar(object):
    FONT_COLOR = (255, 255, 255)
    MIN_RENDER_SIZE = 512

    @classmethod
    def generate(cls, size, fullname, initials, filetype="PNG"):
        """
            Generates a squared avatar with random background color.

            :param size: size of the avatar, in pixels
            :param fullname: fullname to be used to print text and seed the random
            :param filetype: the file format of the image (i.e. JPEG, PNG)
        """
        render_size = max(size, Avatar.MIN_RENDER_SIZE)
        background_color = cls._background_color(fullname)
        image = Image.new('RGBA', (render_size, render_size))
        image = cls._apply_gradient(image, background_color)

        draw = ImageDraw.Draw(image)
        font = cls._font(render_size)
        draw.text(cls._text_position(render_size, initials, font),
                  initials,
                  fill=cls.FONT_COLOR,
                  font=font)
        stream = BytesIO()
        image = image.resize((size, size), Image.ANTIALIAS)
        image.save(stream, format=filetype, optimize=True)
        stream.seek(0)
        return stream

    @staticmethod
    def _apply_gradient(im, color_array):
        def interpolate(f_co, t_co, interval):
            det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
            for i in range(interval):
                yield [round(f + det * i) for f, det in zip(f_co, det_co)]

        gradient = Image.new('RGBA', im.size, color=0)
        draw = ImageDraw.Draw(gradient)

        color_mapper = lambda x: ((255 + x - 100) % 256)

        f_co = (color_array[0], color_array[1], color_array[2])
        t_co = (color_mapper(color_array[0]), color_mapper(color_array[1]), color_mapper(color_array[2]))
        for i, color in enumerate(interpolate(f_co, t_co, im.width * 2)):
            draw.line([(i, 0), (0, i)], tuple(color), width=1)

        return Image.alpha_composite(gradient, im)

    @staticmethod
    def _background_color(s):
        """
            Generate a random background color.
            Brighter colors are dropped, because the text is white.

            :param s: Seed used by the random generator
            (same seed will produce the same color).
        """
        seed(s)
        r = v = b = 255
        while r + v + b > 255*2:
            r = randint(0, 255)
            v = randint(0, 255)
            b = randint(0, 255)
        return (r, v, b)

    @staticmethod
    def _font(size):
        """
            Returns a PIL ImageFont instance.

            :param size: size of the avatar, in pixels
        """
        path = os.path.join(os.path.dirname(__file__), 'data',
                            "Inconsolata.otf")
        return ImageFont.truetype(path, size=int(0.4 * size))

    @staticmethod
    def _text_position(size, text, font):
        """
            Returns the left-top point where the text should be positioned.
        """
        width, height = font.getsize(text)
        left = (size - width) / 2.25
        # I just don't know why 5.5, but it seems to be the good ratio
        top = (size - height) / 2.25
        return left, top



def test(filename, size, fullname, initials):
    bytes = Avatar.generate(size, fullname, initials, "PNG")
    f = open(filename, "wb")
    f.write(bytes.getbuffer())
    f.close()