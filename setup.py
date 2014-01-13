from distutils.core import setup

setup(
    name='image_novice',
    version='0.1.3',
    author='Michael Hansen',
    author_email='hansen.mike@gmail.com',
    packages=['image_novice'],
    url='http://pypi.python.org/pypi/image_novice/',
    license='LICENSE.txt',
    description='A special Python image submodule for beginners.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.7.1",
        "pillow >= 2.1.0",
    ],
)
