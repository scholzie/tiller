#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'name':         'tiller',
        'version':      '0.0.2',
        'description':  'Tiller. Sow your oats.',
        'author':       'Chris Scholz',
        'author_email': 'devops@blueapron.com',
        'install_requires': ['docopt, boto'],
        'packages':     ['tiller'],
        'scripts':      []
        }

setup(**config)
