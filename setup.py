#!/usr/bin/env python

from distutils.core import setup

setup(name='AudioProcessing',
      version='1.0',
      description='Python Distribution Utilities',
      author='Cody',
      author_email='cody@python.net',
      url='https://www.python.org/',
      packages=['audioprocessing'],
      entry_points={  # Optional
            'console_scripts': [
                  'audiobars = audioprocessing.__main__:main',
            ],
      )
