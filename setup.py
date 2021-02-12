# Copyright (c) 2020 - 2020 TomTom N.V. All rights reserved.
#
# This software is the proprietary copyright of TomTom N.V. and its subsidiaries and may be
# used for internal evaluation purposes or commercial use strictly subject to separate
# licensee agreement between you and TomTom. If you are the licensee, you are only permitted
# to use this Software in accordance with the terms of your license agreement. If you are
# not the licensee, then you are not authorized to use this software in any manner and should
# immediately return it to TomTom N.V.

from __future__ import print_function

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='jira-history-api',
    description='Python JIRA Historical Search API',
    long_description=long_description,
    download_url='https://github.com/KevinDeJong-TomTom/jira-history-api',
    url='https://github.com/KevinDeJong-TomTom/jira-history-api',
    author='Kevin de Jong',
    author_email='KevinDeJong@tomtom.com',
    keywords='atlassian jira core software rest api history historical search',
    packages=(
        'jira_history_api',
    ),
    python_requires='>=3.5',
    install_requires=(
        'Click>=7,<8',
        'atlassian-python-api==1.17.2',
    ),
    setup_requires=(
        'setuptools_scm',
        'setuptools_scm_git_archive',
    ),
    use_scm_version={"relative_to": __file__},
    entry_points={
        'console_scripts': [
            'jira-history=jira_history_api.cli:main',
        ]
    },
    zip_safe=True,
)
