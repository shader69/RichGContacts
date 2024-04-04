# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='RichGContacts',
    version="1.0",
    packages=find_packages(),
    author="shader69",
    install_requires=[
        "google", "google_auth_oauthlib", "google-api-python-client",
        "colorama",
        "requests",
        "Pillow",
        "instaloader", "facebook-scraper", "selenium"
    ],
    description="ToFill",
    long_description="ToFill",
    include_package_data=True,
    url='https://github.com/shader69/RichGContacts',
    entry_points={'console_scripts': ['richgcontacts = richgcontacts.__main__:main_for_setup']},
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)