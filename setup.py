from distutils.core import setup

setup(
    name='novice',
    version='0.1.0',
    author='Michael Hansen',
    author_email='hansen.mike@gmail.com',
    packages=['novice'],
    license='LICENSE.txt',
    description='A special Python image submodule for beginners.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.7.1",
        "PIL >= 1.1.7",
    ],
)
