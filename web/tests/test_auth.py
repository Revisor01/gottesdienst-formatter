#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auth-Tests: Login/Logout, geschuetzte Routes, /health Whitelist.
"""
import pytest
import os

os.environ['SECRET_KEY'] = 'test-secret-key-for-unit-tests'


def create_test_app():
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['WTF_CSRF_ENABLED'] = False
    from extensions import db
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def create_test_user(app, username='testuser', password='testpass123', is_admin=False):
    from extensions import db
    from models import User
    with app.app_context():
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    return username, password


class TestProtectedRoutes:
    """Alle bestehenden Routes muessen ohne Login auf /login umleiten."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_test_app()
        self.client = self.app.test_client()

    @pytest.mark.parametrize('path,method', [
        ('/', 'GET'),
        ('/upload', 'POST'),
        ('/download', 'POST'),
        ('/fetch_churchdesk_events', 'POST'),
        ('/export_selected_events', 'POST'),
    ])
    def test_redirect_to_login(self, path, method):
        if method == 'POST':
            resp = self.client.post(path)
        else:
            resp = self.client.get(path)
        assert resp.status_code in (302, 308), f'{path} should redirect, got {resp.status_code}'
        assert '/login' in resp.headers.get('Location', '')

    def test_health_no_login_required(self):
        resp = self.client.get('/health')
        assert resp.status_code == 200


class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_test_app()
        self.client = self.app.test_client()
        create_test_user(self.app)

    def test_login_page_loads(self):
        resp = self.client.get('/login')
        assert resp.status_code == 200
        assert b'Anmelden' in resp.data

    def test_login_success(self):
        resp = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Nach Login sollte Index-Seite kommen (nicht Login-Formular)
        assert b'Anmelden' not in resp.data or b'Abmelden' in resp.data

    def test_login_wrong_password(self):
        resp = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'falsch',
        }, follow_redirects=True)
        assert b'Falscher Benutzername oder Passwort' in resp.data

    def test_login_unknown_user(self):
        resp = self.client.post('/login', data={
            'username': 'gibtsnet',
            'password': 'egal',
        }, follow_redirects=True)
        assert b'Falscher Benutzername oder Passwort' in resp.data

    def test_logout(self):
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
        })
        # Logout
        resp = self.client.get('/logout', follow_redirects=True)
        assert b'Erfolgreich abgemeldet' in resp.data
        # Nach Logout: Index leitet auf Login um
        resp = self.client.get('/')
        assert resp.status_code == 302

    def test_deactivated_user_cannot_login(self):
        from extensions import db
        from models import User
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            user.is_active_user = False
            db.session.commit()
        resp = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
        }, follow_redirects=True)
        # Flask-Login verweigert login_user fuer inaktive User
        assert b'Anmelden' in resp.data
