#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup
import os

setup(
    name='nefit-client',
    version='0.2.2',
    description='Python API and command line tool for talking to the Nefit Easy™ Thermostat',
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    author='Patrick van der Leer',
    author_email='pat.vdleer@gmail.com',
    maintainer='Patrick van der Leer',
    maintainer_email='pat.vdleer@gmail.com',
    url='https://github.com/patvdleer/nefit-client-python.git',
    download_url='https://github.com/patvdleer/nefit-client-python/archive/v0.2.2.tar.gz',
    packages=["nefit"],
    install_requires=['pyaes', 'sleekxmpp'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'nefit-client=nefit.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
