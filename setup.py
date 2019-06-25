#!/usr/bin/env python

import setuptools

setuptools.setup(name='socket-tentacles',
      version='0.0.1',
      description="""Simple tcp client/server that divorces the concept of server/client from which side opens the tcp connection.""",
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/tentacles',
      packages=setuptools.find_packages()
  )
