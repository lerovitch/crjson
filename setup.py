# -*- coding:utf-8 -*-
from distutils.core import setup

setup(
    name = 'crjson',
    version = '1.1',
    author = 'Sergi Sorribas',
    author_email = 'ssorribas@gmail.com',
    packages = ['crjson', 'crjson.backends'],
    url = 'https://github.com/lerovitch/crjson',
    license = 'LICENSE.txt',
    description = 'Iterative JSON parser with a standard Python iterator interface',
    long_description = open('README.rst').read(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
