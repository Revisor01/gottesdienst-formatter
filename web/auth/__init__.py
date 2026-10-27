#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auth-Blueprint für Login und Logout."""
from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='')

from auth import routes  # noqa: E402, F401
