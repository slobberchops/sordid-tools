#
# Copyright 2017 Rafe Kaplan
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
#

import os

import pkg_resources
import setuptools


def parse_requirements():
    requirements_txt = str(pkg_resources.resource_string(__name__, 'requirements.txt'), 'utf-8')
    requirements_lines = requirements_txt.split(os.linesep)
    requirements_lines = [l.strip() for l in requirements_lines]
    requirements_lines = [l for l in requirements_lines if not l.startswith(('#'))]
    requirements_lines = [l for l in requirements_lines if l]
    return requirements_lines


requirements = parse_requirements()

setuptools.setup(
    name='sordid-wsgi',
    version='0.1',
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    license='Apache License, Version 2.0',
    url='https://github.com/slobberchops/sordid-tools/tree/master/wsgi',
)
