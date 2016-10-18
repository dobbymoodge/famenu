"""FVWM-Alike Menu, a simple GUI menu backgrounder

See:
https://github.com/dobbymoodge/famenu
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


try:
    import tkinter
except ImportError:
    sys.exit("tkinter not found")

setup(
    name='famenu',

    version='0.1',

    description='Hotkey-accessible general-purpose menus that run in the background',
    long_description=long_description,
    url='https://github.com/dobbymoodge/famenu',
    author='John Lamb',
    author_email='john.w.lamb@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Desktop Environment',

        'License :: OSI Approved :: MIT License',  # TODO: pick the right one

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='menu desktop',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['python-xlib'],
    entry_points={
        'console_scripts': [
            'famenu=famenu:main',
        ],
    },
)
