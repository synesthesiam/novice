import os
from PIL import Image
from itertools import repeat, islice, product

class novice:
    @staticmethod
    def open(path):
        """
        Creates a new picture object from the given image path
        """
        return novice.picture(os.path.abspath(path))

# ================================================== 

    class pixel(object):
        def __init__(self, pic, data, x, y, rgb):
            self.__picture = pic
            self.__data = data
            self.__x = x
            self.__y = y
            self.__red = rgb[0] / 255.0
            self.__green = rgb[1] / 255.0
            self.__blue = rgb[2] / 255.0

        @property
        def x(self):
            """Gets the horizontal location (left = 0)"""
            return self.__x

        @property
        def y(self):
            """Gets the vertical location (bottom = 0)"""
            return self.__y

        @property
        def red(self):
            """Gets or sets the red component"""
            return self.__red

        @red.setter
        def red(self, value):
            self.__validate(value)
            self.__red = value
            self.__setpixel()

        @property
        def green(self):
            """Gets or sets the green component"""
            return self.__green

        @green.setter
        def green(self, value):
            self.__validate(value)
            self.__green = value
            self.__setpixel()

        @property
        def blue(self):
            """Gets or sets the blue component"""
            return self.__blue

        @blue.setter
        def blue(self, value):
            self.__validate(value)
            self.__blue = value
            self.__setpixel()

        @property
        def rgb(self):
            return (self.red, self.green, self.blue)

        @rgb.setter
        def rgb(self, value):
            """Gets or sets the color with an (r, g, b) tuple"""
            for v in value:
                self.__validate(v)

            self.__red = value[0]
            self.__green = value[1]
            self.__blue = value[2]
            self.__setpixel()

        def __validate(self, pixel):
            """Verifies that the pixel value is in [0, 1]"""
            try:
                pixel = float(pixel)
                if (pixel < 0) or (pixel > 1):
                    raise ValueError()
            except ValueError:
                raise ValueError("Expected a number between 0 and 1, but got {0} instead!".format(pixel))

        def __setpixel(self):
            """
            Sets the actual pixel value in the picture.
            NOTE: Using Cartesian coordinate system!
            """
            self.__data[self.__x, self.__picture.height - self.__y - 1] = \
                    (int(self.red * 255), int(self.green * 255), int(self.blue * 255))

            # Modified pictures lose their paths
            self.__picture._picture__path = None
            self.__picture._picture__modified = True

        def __repr__(self):
            return "pixel (red: {0}, green: {1}, blue: {2})".format(self.red, self.green, self.blue)

# ================================================== 

    class picture(object):
        def __init__(self, path):
            self.__path = path
            image = Image.open(path)
            self.__format = image.format

            # We convert the image to RGB automatically so
            # (r, g, b) tuples can be used everywhere.
            self.__image = image.convert("RGB")
            self.__data = self.__image.load()
            self.__modified = False

        def save(self, path):
            """Saves the picture to the given path."""
            self.__image.save(path)
            self.__modified = False
            self.__path = os.path.abspath(path)

            # Need to re-open the image to get the format
            # for some reason (likely because we converted to RGB).
            self.__format = Image.open(path).format

        @property
        def path(self):
            """Gets the path of the picture"""
            return self.__path

        @property
        def modified(self):
            """Gets a value indicating if the picture has changed"""
            return self.__modified

        @property
        def format(self):
            """Gets the format of the picture (e.g., PNG)"""
            return self.__format

        @property
        def size(self):
            """Gets or sets the size of the picture with a (width, height) tuple"""
            return self.__image.size

        @size.setter
        def size(self, value):
            try:
                # Don't resize if no change in size
                if (value[0] != self.width) or (value[1] != self.height):
                    self.__image = self.__image.resize(value)
                    self.__data = self.__image.load()
                    self.__modified = True
                    self.__path = None
            except TypeError:
                raise TypeError("Expected (width, height), but got {0} instead!".format(value))

        @property
        def width(self):
            """Gets or sets the width of the image (maintains correct aspect)"""
            return self.size[0]

        @width.setter
        def width(self, value):
            aspect = float(self.width) / float(self.height)
            self.size = (value, int(value / aspect))

        @property
        def height(self):
            """Gets or sets the height of the image (maintains correct aspect)"""
            return self.size[1]

        @height.setter
        def height(self, value):
            aspect = float(self.width) / float(self.height)
            self.size = (int(value * aspect), value)

        def __makepixel(self, x, y):
            """
            Creates a novice.pixel object for a given x, y location.
            NOTE: Using Cartesian coordinate system!
            """
            rgb = self.__data[x, self.height - y - 1]
            return novice.pixel(self, self.__data, x, y, rgb)

        def __iter__(self):
            """Iterates over all pixels in the image"""
            for x in xrange(self.width):
                for y in xrange(self.height):
                    yield self.__makepixel(x, y)

        def __getpixels(self, xs, ys):
            """
            Yields pixel objects for the product of the x and y iterators.
            It's critical that product() is used here because one of the
            iterators may repeat forever.
            """
            for (x, y) in product(xs, ys):
                yield self[x, y]

        def __getitem__(self, key):
            """Gets pixels using 2D int or slice notations"""
            if isinstance(key, tuple):

                # self[x, y]
                if isinstance(key[0], int) and isinstance(key[1], int):
                    x = key[0]
                    y = key[1]
                    if ((x < 0) or (x >= self.width) or
                        (y < 0) or (y >= self.height)):
                        raise IndexError("Index out of range")                        

                    return self.__makepixel(x, y)

                # self[x, ystart:ystop:ystep]
                elif isinstance(key[0], int) and isinstance(key[1], slice):
                    sly = key[1]
                    return self.__getpixels(repeat(key[0]),
                                            islice(xrange(self.height), sly.start, sly.stop, sly.step))

                # self[xstart:xstop:xstep, y]
                elif isinstance(key[0], slice) and isinstance(key[1], int):
                    slx = key[0]
                    return self.__getpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                            repeat(key[1]))

                # self[xstart:xstop:xstep, ystart:ystop:ystep]
                elif isinstance(key[0], slice) and isinstance(key[1], slice):
                    slx = key[0]
                    sly = key[1]
                    return self.__getpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                            islice(xrange(self.height), sly.start, sly.stop, sly.step))

            raise TypeError("Invalid key type")

        def __setpixels(self, xs, ys, value):
            """
            Sets pixel values for locations in the product of the x and y iterators.
            It's critical that product() is used here because one of the
            iterators may repeat forever.
            """
            for (x, y) in product(xs, ys):
                pixel = self[x, y]
                pixel.rgb = value

        def __setitem__(self, key, value):
            """Sets pixelvalues using 2D int or slice notations"""
            if isinstance(key, tuple):

                # self[x, y]
                if isinstance(key[0], int) and isinstance(key[1], int):
                    pixel = self[key[0], key[1]]
                    pixel.rgb = value

                # self[x, ystart:ystop:ystep]
                elif isinstance(key[0], int) and isinstance(key[1], slice):
                    sly = key[1]
                    self.__setpixels(repeat(key[0]),
                                     islice(xrange(self.height), sly.start, sly.stop, sly.step),
                                     value)

                # self[xstart:xstop:xstep, y]
                elif isinstance(key[0], slice) and isinstance(key[1], int):
                    slx = key[0]
                    self.__setpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                     repeat(key[1]),
                                     value)

                # self[xstart:xstop:xstep, ystart:ystop:ystep]
                elif isinstance(key[0], slice) and isinstance(key[1], slice):
                    slx = key[0]
                    sly = key[1]
                    self.__setpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                     islice(xrange(self.height), sly.start, sly.stop, sly.step),
                                     value)
            else:
                raise TypeError("Invalid key type")

        def __repr__(self):
            return "picture (format: {0}, path: {1}, modified: {2})".format(self.format, self.path, self.modified)

