#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup
import os

setup(
    name='nefit-client',
    version='0.2.1',
    description='Python API and command line tool for talking to the Nefit Easy™ Thermostat',
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    author='Patrick van der Leer',
    author_email='pat.vdleer@gmail.com',
    maintainer='Patrick van der Leer',
    maintainer_email='pat.vdleer@gmail.com',
    url='https://github.com/patvdleer/nefit-client-python.git',
    download_url='https://github.com/patvdleer/nefit-client-python/archive/v0.2.1.tar.gz',
    packages=["nefit"],
    install_requires=['pyaes', 'sleekxmpp']
)
