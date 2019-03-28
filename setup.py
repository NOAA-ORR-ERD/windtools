#!/usr/bin/env python

from setuptools import setup
import glob

requirements = [
    # package requirements go here
]

setup(
    name='windtools',
    version='0.1.0',
    description="handy utilities for workign with wind data",
    author="Christopher H. Barker",
    author_email='Chris.Barker@noaa.gov',
    url='https://github.com/NOAA-ORR-ERD/windtools',
    packages=['windtools'],
    scripts = glob.glob("windtools/scripts/*"),
    # entry_points={
    #     'console_scripts': [
    #         'windtools=windtools.cli:cli'
    #     ]
    # },
    install_requires=requirements,
    keywords='windtools',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)
