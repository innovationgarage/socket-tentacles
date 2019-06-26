#!/usr/bin/env python

import setuptools

setuptools.setup(name='socket-tentacles',
      version='0.0.4',
      description="""Simple tcp client/server that divorces the concept of server/client from which side opens the tcp connection.""",
      long_description="""Simple thread based tcp client/server that divorces the concept of server/client from which side opens the tcp connection. Configured using a simple dictionary structure that can be easily read from json.""",
      author='Egil Moeller',
      author_email='egil@innovationgarage.no',
      url='https://github.com/innovationgarage/socket-tentacles',
      packages=setuptools.find_packages()
  )
