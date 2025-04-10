#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-razorpay',
      version='0.0.2',
      description='Singer.io tap for extracting data from the Amazon Advertising API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_razorpay'],
      install_requires=[
          'tap-framework @ git+https://github.com/hotgluexyz/tap-framework.git#egg=tap-framework', # USING THE HOTGLUE VERSION
      ],
      entry_points='''
          [console_scripts]
          tap-razorpay=tap_razorpay:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_razorpay': [
              'schemas/*.json'
          ]
      })
