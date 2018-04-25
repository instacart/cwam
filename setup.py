#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.7',
    'boto3>=1.4.3',
    'dictdiffer>=0.6.1',
    'PyYAML>=3.12'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='cwam',
    version='1.0.0',
    description="Easy way to create default CloudWatch Alarms.",
    long_description=readme + '\n\n' + history,
    author="Quentin Rousseau",
    author_email='quentin@instacart.com',
    url='https://github.com/instacart/cwam',
    packages=[
        'cwam',
    ],
    package_dir={'cwam':
                 'cwam'},
    entry_points={
        'console_scripts': [
            'cwam=cwam.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='cloudwatch',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: System :: Monitoring'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
