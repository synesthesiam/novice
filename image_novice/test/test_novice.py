#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for novice submodule.
:license: modified BSD
"""

import os, tempfile
import numpy as np
import image_novice as novice
from numpy.testing import TestCase, assert_equal, assert_raises, assert_allclose

def _array_2d_to_RGB(array):
    return np.tile(array[:, :, np.newaxis], (1, 1, 3))

class TestNovice(TestCase):
    sample_path = "sample.png"
    small_sample_path = "block.png"

    def test_pic_info(self):
        pic = novice.open(self.sample_path)
        assert_equal(pic.format, "png")
        assert_equal(pic.path, os.path.abspath(self.sample_path))
        assert_equal(pic.size, (665, 500))
        assert_equal(pic.width, 665)
        assert_equal(pic.height, 500)
        assert_equal(pic.modified, False)
        assert_equal(pic.inflation, 1)

        num_pixels = sum(1 for p in pic)
        assert_equal(num_pixels, pic.width * pic.height)

    def test_pixel_iteration(self):
        pic = novice.open(self.small_sample_path)
        num_pixels = sum(1 for p in pic)
        assert_equal(num_pixels, pic.width * pic.height)

    def test_modify(self):
        pic = novice.open(self.small_sample_path)
        assert_equal(pic.modified, False)

        for p in pic:
            if p.x < (pic.width / 2):
                p.red /= 2
                p.green /= 2
                p.blue /= 2

        for p in pic:
            if p.x < (pic.width / 2):
                assert_equal(p.red <= 128, True)
                assert_equal(p.green <= 128, True)
                assert_equal(p.blue <= 128, True)

        s = pic.size
        pic.size = (pic.width / 2, pic.height / 2)
        assert_equal(pic.size, (int(s[0] / 2), int(s[1] / 2)))

        assert_equal(pic.modified, True)
        assert_equal(pic.path, None)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            pic.save(tmp.name)

            assert_equal(pic.modified, False)
            assert_equal(pic.path, os.path.abspath(tmp.name))
            assert_equal(pic.format, "jpeg")

    def test_pixel_rgb(self):
        pic = novice.Picture.from_size((3, 3), color=(10, 10, 10))
        pixel = pic[0, 0]
        pixel.rgb = np.arange(3)

        assert_equal(pixel.rgb, np.arange(3))
        for i, channel in enumerate((pixel.red, pixel.green, pixel.blue)):
            assert_equal(channel, i)

        pixel.red = 3
        pixel.green = 4
        pixel.blue = 5
        assert_equal(pixel.rgb, np.arange(3) + 3)

        for i, channel in enumerate((pixel.red, pixel.green, pixel.blue)):
            assert_equal(channel, i + 3)

    def test_pixel_rgb_float(self):
        pixel = novice.Picture.from_size((1, 1))[0, 0]
        pixel.rgb = (1.1, 1.1, 1.1)
        assert_equal(pixel.rgb, (1, 1, 1))

    def test_modified_on_set(self):
        pic = novice.Picture(self.small_sample_path)
        pic[0, 0] = (1, 1, 1)
        assert pic.modified
        assert pic.path is None

    def test_modified_on_set_pixel(self):
        data = np.zeros(shape=(10, 5, 3), dtype=np.uint8)
        pic = novice.Picture(array=data)

        pixel = pic[0, 0]
        pixel.green = 1
        assert pic.modified

    def test_update_on_save(self):
        pic = novice.Picture(array=np.zeros((3, 3, 3)))
        pic.size = (6, 6)
        assert pic.modified
        assert pic.path is None

        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            pic.save(tmp.name)

            assert not pic.modified
            assert_equal(pic.path, os.path.abspath(tmp.name))
            assert_equal(pic.format, "jpeg")

    def test_indexing(self):
        pic = novice.open(self.small_sample_path)

        # Slicing
        pic[0:5, 0:5] = (0, 0, 0)
        for p in pic:
            if (p.x < 5) and (p.y < 5):
                assert_equal(p.rgb, (0, 0, 0))
                assert_equal(p.red, 0)
                assert_equal(p.green, 0)
                assert_equal(p.blue, 0)

        pic[:5, :5] = (255, 255, 255)
        for p in pic:
            if (p.x < 5) and (p.y < 5):
                assert_equal(p.rgb, (255, 255, 255))
                assert_equal(p.red, 255)
                assert_equal(p.green, 255)
                assert_equal(p.blue, 255)

        pic[5:pic.width, 5:pic.height] = (255, 0, 255)
        for p in pic:
            if (p.x >= 5) and (p.y >= 5):
                assert_equal(p.rgb, (255, 0, 255))
                assert_equal(p.red, 255)
                assert_equal(p.green, 0)
                assert_equal(p.blue, 255)

        pic[5:, 5:] = (0, 0, 255)
        for p in pic:
            if (p.x >= 5) and (p.y >= 5):
                assert_equal(p.rgb, (0, 0, 255))
                assert_equal(p.red, 0)
                assert_equal(p.green, 0)
                assert_equal(p.blue, 255)

        # Outside bounds
        assert_raises(IndexError, lambda: pic[pic.width, pic.height])

        # Negative indexing not supported
        assert_raises(IndexError, lambda: pic[-1, -1])
        assert_raises(IndexError, lambda: pic[-1:, -1:])

    def test_picture_slice(self):
        array = _array_2d_to_RGB(np.arange(0, 10)[np.newaxis, :])
        pic = novice.Picture(array=array)

        x_slice = slice(3, 8)
        subpic = pic[:, x_slice]
        assert_allclose(subpic._image, array[x_slice, :])

    def test_move_slice(self):
        h, w = 3, 12
        array = _array_2d_to_RGB(np.linspace(0, 255, h * w).reshape(h, w))
        array = array.astype(np.uint8)

        pic = novice.Picture(array=array)
        pic_orig = novice.Picture(array=array.copy())

        # Move left cut of image to the right side.
        cut = 5
        rest = pic.width - cut
        temp = pic[:cut, :]
        temp._image = temp._image.copy()
        pic[:rest, :] = pic[cut:, :]
        pic[rest:, :] = temp

        assert_equal(pic[rest:, :]._image, pic_orig[:cut, :]._image)
        assert_equal(pic[:rest, :]._image, pic_orig[cut:, :]._image)

    #def test_negative_index(self):
        #n = 10
        #array = _array_2d_to_RGB(np.arange(0, n)[np.newaxis, :])
        ## Test both x and y indices.
        #pic = novice.Picture(array=array)
        #assert_equal(pic[-1, 0]._image, pic[n - 1, 0]._image)
        #pic = novice.Picture(array=rgb_transpose(array))
        #assert_equal(pic[0, -1]._image, pic[0, n - 1]._image)

    #def test_negative_slice(self):
        #n = 10
        #array = _array_2d_to_RGB(np.arange(0, n)[np.newaxis, :])
        ## Test both x and y slices.
        #pic = novice.Picture(array=array)
        #assert_equal(pic[-3:, 0]._image, pic[n - 3:, 0]._image)
        #pic = novice.Picture(array=rgb_transpose(array))
        #assert_equal(pic[0, -3:]._image, pic[0, n - 3:]._image)

    def test_getitem_with_step(self):
        h, w = 5, 5
        array = _array_2d_to_RGB(np.linspace(0, 255, h * w).reshape(h, w))
        pic = novice.Picture(array=array)
        sliced_pic = pic[::2, ::2]
        assert_equal(sliced_pic._image, novice.Picture(array=array[::2, ::2])._image)

    def test_slicing(self):
        cut = 40
        pic = novice.open(self.sample_path)
        rest = pic.width - cut
        temp = pic[:cut, :].copy()
        pic[:rest, :] = pic[cut:, :]
        pic[rest:, :] = temp

