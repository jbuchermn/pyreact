#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pyreact',
      version='0.0.1',
      description='PyReact',
      author='Jonas Bucher',
      author_email='j.bucher.mn@gmail.com',
      install_required=["websockets"],
      packages=find_packages(
          exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      license='LICENSE.txt',
      )
