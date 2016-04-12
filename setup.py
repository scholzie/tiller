#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'description':  'Tiller. Sow your oats.',
        'author':       'Chris Scholz',
        'author_email': 'devops@blueapron.com',
        'version':      '0.0.1',
        'install_requires': ['nose'],
        'packages':     ['tiller'],
        'scripts':      [],
        'name':         'tiller'
        }

setup(**config)
