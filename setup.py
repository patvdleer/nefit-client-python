#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup

setup(
    name='nefit-client',
    version='0.2',
    description='Python API and command line tool for talking to the Nefit Easy™ Thermostat',
    author='Patrick van der Leer',
    author_email='pat.vdleer@gmail.com',
    maintainer='Patrick van der Leer',
    maintainer_email='pat.vdleer@gmail.com',
    url='https://github.com/patvdleer/nefit-client-python.git',
    packages=["nefit"],
    install_requires=['pycrypto', 'sleekxmpp']
)
