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


class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    smtp_server = db.Column(db.String(256), default='')
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(256), default='')
    smtp_password_encrypted = db.Column(db.Text, default='')
    sender_email = db.Column(db.String(256), default='')
    recipient_email = db.Column(db.String(256), default='')
    send_day = db.Column(db.Integer, default=18)  # 1-28, Tag des Monats fuer Auto-Versand
    auto_send_enabled = db.Column(db.Boolean, default=False)
    last_send_date = db.Column(db.DateTime, nullable=True)
    last_send_status = db.Column(db.String(512), nullable=True)

    user = db.relationship('User', backref=db.backref('settings', uselist=False, lazy=True))


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)  # ChurchDesk org ID (e.g. 2596)
    name = db.Column(db.String(256), nullable=False)
    token = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return '<Organization {} {}>'.format(self.id, self.name)


class ServiceTypeMapping(db.Model):
    __tablename__ = 'service_type_mappings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(256), unique=True, nullable=False)
    output_label = db.Column(db.String(256), nullable=False)
    priority = db.Column(db.Integer, default=100, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return '<ServiceTypeMapping {} -> {}>'.format(self.keyword, self.output_label)
