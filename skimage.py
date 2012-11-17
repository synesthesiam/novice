import os
from PIL import Image
from itertools import repeat, islice, izip

class novice:
    @staticmethod
    def open(path):
        return novice.picture(os.path.abspath(path))

    class pixel(object):
        def __init__(self, pic, image, x, y, rgb):
            self.__picture = pic
            self.__image = image
            self.__x = x
            self.__y = y
            self.__red = rgb[0] / 255.0
            self.__green = rgb[1] / 255.0
            self.__blue = rgb[2] / 255.0

        @property
        def x(self):
            return self.__x

        @property
        def y(self):
            return self.__y

        @property
        def red(self):
            return self.__red

        @red.setter
        def red(self, value):
            self.__validate(value)
            self.__red = value
            self.__setpixel()

        @property
        def green(self):
            return self.__green

        @green.setter
        def green(self, value):
            self.__validate(value)
            self.__green = value
            self.__setpixel()

        @property
        def blue(self):
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
            for v in value:
                self.__validate(v)

            self.__red = value[0]
            self.__green = value[1]
            self.__blue = value[2]
            self.__setpixel()

        def __validate(self, pixel):
            try:
                pixel = float(pixel)
                if (pixel < 0) or (pixel > 1):
                    raise ValueError()
            except ValueError:
                raise ValueError("Expected a number between 0 and 1, but got {0} instead!".format(pixel))

        def __setpixel(self):
            self.__image.putpixel((self.__x, self.__y),
                    (int(self.red * 255), int(self.green * 255), int(self.blue * 255)))
            self.__picture._picture__modified = True

        def __repr__(self):
            return "pixel (red: {0}, green: {1}, blue: {2})".format(self.red, self.green, self.blue)

    class picture(object):
        def __init__(self, path):
            self.__path = path
            self.__image = Image.open(path).convert("RGB")
            self.format = self.__image.format
            self.__modified = False

        def save(self, path):
            self.__image.save(path)
            self.__modified = False
            self.__path = path

        @property
        def path(self):
            return self.__path

        @property
        def modified(self):
            return self.__modified

        @property
        def size(self):
            return self.__image.size

        @size.setter
        def size(self, value):
            try:
                # Don't resize if no change in size
                if (value[0] != self.width) or (value[1] != self.height):
                    self.__image = self.__image.resize(value)
                    self.__modified = True
                    self.__path = None
            except TypeError:
                raise TypeError("Expected (width, height), but got {0} instead!".format(value))

        @property
        def width(self):
            return self.size[0]

        @width.setter
        def width(self, value):
            aspect = float(self.width) / float(self.height)
            self.size = (value, int(value / aspect))

        @property
        def height(self):
            return self.size[1]

        @height.setter
        def height(self, value):
            aspect = float(self.width) / float(self.height)
            self.size = (int(value * aspect), value)

        def __makepixel(self, x, y):
            rgb = self.__image.getpixel((x, y))
            return novice.pixel(self, self.__image, x, y, rgb)

        def __iter__(self):
            for x in xrange(self.width):
                for y in xrange(self.height):
                    yield self.__makepixel(x, y)

        def __getpixels(self, xs, ys):
            for (x, y) in izip(xs, ys):
                yield self[x, y]

        def __getitem__(self, key):
            if isinstance(key, tuple):
                if isinstance(key[0], int) and isinstance(key[1], int):
                    x = key[0]
                    y = key[1]
                    if ((x < 0) or (x >= self.width) or
                        (y < 0) or (y >= self.height)):
                        raise IndexError("Index out of range")                        

                    return self.__makepixel(x, y)

                elif isinstance(key[0], int) and isinstance(key[1], slice):
                    sly = key[1]
                    return self.__getpixels(repeat(key[0]),
                                            islice(xrange(self.height), sly.start, sly.stop, sly.step))

                elif isinstance(key[0], slice) and isinstance(key[1], int):
                    slx = key[0]
                    return self.__getpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                            repeat(key[1]))

                elif isinstance(key[0], slice) and isinstance(key[1], slice):
                    slx = key[0]
                    sly = key[1]
                    return self.__getpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                            islice(xrange(self.height), sly.start, sly.stop, sly.step))

            raise TypeError("Invalid key type")

        def __setpixels(self, xs, ys, value):
            for (x, y) in izip(xs, ys):
                pixel = self[x, y]
                pixel.rgb = value

        def __setitem__(self, key, value):
            if isinstance(key, tuple):
                if isinstance(key[0], int) and isinstance(key[1], int):
                    pixel = self[key[0], key[1]]
                    pixel.rgb = value

                elif isinstance(key[0], int) and isinstance(key[1], slice):
                    sly = key[1]
                    self.__setpixels(repeat(key[0]),
                                     islice(xrange(self.height), sly.start, sly.stop, sly.step),
                                     value)

                elif isinstance(key[0], slice) and isinstance(key[1], int):
                    slx = key[0]
                    self.__setpixels(islice(xrange(self.width), slx.start, slx.stop, slx.step),
                                     repeat(key[1]),
                                     value)

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


if __name__ == "__main__":
    picture = novice.open("sample.png")
    print "Format:", picture.format
    print "Path:", picture.path
    print "Size:", picture.size
    print "Modified:", picture.modified

    print ""
    print "Changing width"
    picture.width = picture.width / 2
    print "Path:", picture.path
    print "Size:", picture.size
    print "Modified:", picture.modified

    print ""
    print "Saving"
    picture.save("sample-small.jpg")
    print "Path:", picture.path
    print "Size:", picture.size
    print "Modified:", picture.modified

    print ""
    print "Changing pixels"
    for pixel in picture:
        if (pixel.red > 0.5) and (pixel.x < picture.width):
            pixel.red /= 2 

    print "Modified:", picture.modified
    picture.save("sample-halfred.jpg")
    print "Path:", picture.path
