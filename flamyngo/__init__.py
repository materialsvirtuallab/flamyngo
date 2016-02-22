# coding: utf-8
# Copyright (c) Materials Virtual Lab.
# Distributed under the terms of the BSD License.

from __future__ import division, unicode_literals, print_function

"""
#TODO: Replace with proper module doc.
"""

from flask import Flask

app = Flask(__name__)

from . import views
