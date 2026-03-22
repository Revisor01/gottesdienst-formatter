#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Datenbankmodelle fuer die Gottesdienst-Formatter Web-App.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        # Ueberschreibt UserMixin.is_active — Flask-Login prueft diesen Wert automatisch.
        # Das DB-Feld heisst is_active_user um Konflikte mit der Property zu vermeiden.
        return self.is_active_user

    def __repr__(self):
        return '<User {}>'.format(self.username)
