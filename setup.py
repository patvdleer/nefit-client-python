#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup
from nefit.version import version
import os

setup(
    name='nefit-client',
    version=version,
    description='Python API and command line tool for talking to the Nefit Easy™ Thermostat',
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author='Patrick van der Leer',
    author_email='pat.vdleer@gmail.com',
    maintainer='Patrick van der Leer',
    maintainer_email='pat.vdleer@gmail.com',
    url='https://github.com/patvdleer/nefit-client-python.git',
    download_url='https://github.com/patvdleer/nefit-client-python/archive/v%s.tar.gz' % version,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
