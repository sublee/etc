# -*- coding: utf-8 -*-
"""
etc
~~~

An etcd client library for humans.

"""
import os

from setuptools import find_packages, setup
from setuptools.command.test import test


# Include __about__.py.
__dir__ = os.path.dirname(__file__)
about = {}
with open(os.path.join(__dir__, 'etc', '__about__.py')) as f:
    exec(f.read(), about)


# Use pytest instead.
def run_tests(self):
    raise SystemExit(__import__('pytest').main(['-v']))
test.run_tests = run_tests


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
    packages=find_packages(),
    zip_safe=False,  # I don't like egg.
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Topic :: Software Development'],
    install_requires=['iso8601', 'requests>=2.8.0'],
    tests_require=['pytest'],
    test_suite='...',
)
