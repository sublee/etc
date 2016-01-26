# -*- coding: utf-8 -*-
"""
etc
~~~

An etcd client library for humans.

"""
from setuptools import setup


about = {'__version__': '0.0.0-dev',
         '__license__': 'BSD',
         '__author__': 'Heungsub Lee',
         '__author_email__': 'sub@subl.ee',
         '__url__': 'https://github.com/sublee/etc',
         '__description__': 'An etcd client library for humans'}


setup(
    name='etc',
    version=about['__version__'],
    license=about['__license__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    description=about['__description__'],
    long_description=__doc__,
    platforms='any',
    packages=['etc'],
    zip_safe=False,  # I don't like egg.
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Topic :: Software Development'],
)
