# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
from setuptools import setup, find_packages


# Helpers
def read(path):
    basedir = os.path.dirname(__file__)
    return io.open(os.path.join(basedir, path), encoding='utf-8').read()


# Prepare
readme = read('README.md')
license = read('LICENSE.txt')
requirements = read('requirements.txt')
requirements_dev = read('requirements.dev.txt')
package = json.loads(read('package.json'))


# Run
setup(
    name=package['name'],
    version=package['version'],
    description=package['description'],
    long_description=readme,
    author=package['author'],
    author_email=package['author_email'],
    url=package['repository'],
    license=package['license'],
    packages=find_packages(exclude=['examples', 'tests']),
    package_dir={package['slug']: package['slug']},
    include_package_data=True,
    install_requires=requirements,
    tests_require=requirements_dev,
    zip_safe=False,
    keywords=package['keywords'],
    classifiers=package['classifiers'],
    entry_points={
        'console_scripts': [
            'openspending = oscli:cli',
            'os = oscli:cli'
        ]
    }
)
