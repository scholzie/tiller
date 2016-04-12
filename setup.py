#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'name':         'tiller',
        'version':      '0.0.1',
        'description':  'Tiller. Sow your oats.',
        'author':       'Chris Scholz',
        'author_email': 'devops@blueapron.com',
        'install_requires': ['nose'],
        'packages':     ['tiller'],
        'scripts':      []
        }

setup(**config)
