Image Novice
============
A special Python image submodule for beginners.

Description
-----------
novice is a simple wrapper around the Python Image Library (PIL) for beginners.
It allows for easy loading, manipulating, and saving of image files.

**NOTE: This module uses the Cartesian coordinate system!**

Example
-------

    >>> import novice                         # special submodule for beginners

    >>> picture = novice.open('sample.png')   # create a picture object from a file
    >>> print picture.format                  # pictures know their format...
    'png'
    >>> print picture.path                    # ...and where they came from...
    '/Users/example/sample.png'
    >>> print picture.size                    # ...and their size
    (665, 500)
    >>> print picture.width                   # 'width' and 'height' also exposed
    665
    >>> picture.size = (200, 250)             # changing size automatically resizes
    >>> for pixel in picture:                 # can iterate over pixels
    >>> ... if ((pixel.red > 128) and         # pixels have RGB (values are 0-255)...
    >>> ...     (pixel.x < picture.width)):   # ...and know where they are
    >>> ...     pixel.red /= 2                # pixel is an alias into the picture
    >>> ...
    >>> print picture.modified                # pictures know if their pixels are dirty
    True
    >>> print picture.path                    # picture no longer corresponds to file
    None
    >>> picture[0:20, 0:20] = (0, 0, 0)       # overwrite lower-left rectangle with black
    >>> picture.save('sample-bluegreen.jpg')  # guess file type from suffix
    >>> print picture.path                    # picture now corresponds to file
    '/Users/example/sample-bluegreen.jpg'
    >>> print picture.format                  # ...has a different format
    jpeg
    >>> print picture.modified                # and is now in sync
    False
