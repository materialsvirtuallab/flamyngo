# coding: utf-8
# Copyright (c) Materials Virtual Lab
# Distributed under the terms of the BSD License.

import glob
import os
from io import open

from setuptools import setup, find_packages

SETUP_PTH = os.path.dirname(os.path.abspath(__file__))

long_desc = """
Flamyngo is a customizable Flask frontend for MongoDB.

At the most basic level, the aim is to delegate most settings to a YAML
configuration file, which then allows the  underlying code to be reused for
any conceivable collection.

Detailed usage instructions are available at the project's `Github page
<https://github.com/materialsvirtuallab/flamyngo>`_.
"""

setup(
    name="flamyngo",
    packages=find_packages(),
    version="0.9.2",
    install_requires=["flask", "pyyaml", "monty>=0.7.0", "pymongo"],
    package_data={"flamyngo": ["static/*.*", "static/js/*.*",
                               "templates/*"]},
    author="Shyue Ping Ong",
    author_email="ongsp@eng.ucsd.edu",
    maintainer="Shyue Ping Ong",
    maintainer_email="ongsp@eng.ucsd.edu",
    url="https://github.com/materialsvirtuallab/flamyngo",
    license="BSD",
    description="Flamyngo is a customizable Flask frontend for MongoDB.",
    long_description=long_desc,
    keywords=["flask", "web", "frontend", "gui", "MongoDB"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points={
          'console_scripts': [
              'flm = flamyngo.flm:main'
          ]
    }
)
