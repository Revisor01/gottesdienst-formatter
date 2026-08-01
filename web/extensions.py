#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask-Extensions als Singletons — werden in create_app() per init_app() an die App gebunden.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte einloggen.'
login_manager.login_message_category = 'info'
