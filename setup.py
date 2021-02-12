# Copyright (c) 2020 - 2021 TomTom N.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    license='Apache License 2.0',
    license_files='LICENSE.txt',
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
