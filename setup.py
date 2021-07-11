#!/usr/bin/env python

import os
from setuptools import find_packages, setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='lissi',
	version='0.0.1b1',
	description='IRC bot expandable via plugins',
    license = 'GPLV2',
	author='Gentoo Linux Forums Team',
	author_email='forum-mods@gentoo.org',
	url='https://github.com/fedeliallalinea/lissi',
#	long_description=read('README.md'),
	project_urls={
        'Bug Reports': 'https://github.com/fedeliallalinea/lissi/issues',
        'Source': 'https://github.com/fedeliallalinea/lissi',
	},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Chat :: Internet Relay Chat'
    ],
    python_requires='>=3.6',
    install_requires=[
        'beautifulsoup>=4',
        'requests'
    ],
    packages=find_packages(),
    data_files = [
        ('/etc', ['etc/lissi.cfg'])
    ],
    entry_points={
        'console_scripts': [
            'lissi = lissi.lissi:main'
        ]
    }
)