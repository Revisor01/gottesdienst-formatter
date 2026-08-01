#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin-Tests: Zugriffskontrolle, User-CRUD, CLI create-admin.
"""
import pytest
import os

os.environ['SECRET_KEY'] = 'test-secret-key-for-unit-tests'


def create_test_app():
    from sqlalchemy.pool import StaticPool
    from app import create_app
    app = create_app(test_config={
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        # StaticPool: alle Connections teilen dieselbe In-Memory SQLite DB
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
    })
    from extensions import db
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)


def create_user(app, username, password, is_admin=False):
    from extensions import db
    from models import User
    with app.app_context():
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


class TestAdminAccess:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_test_app()
        self.client = self.app.test_client()
        create_user(self.app, 'admin', 'adminpass1', is_admin=True)
        create_user(self.app, 'normal', 'normalpass1', is_admin=False)

    def test_admin_can_access_users(self):
        login(self.client, 'admin', 'adminpass1')
        resp = self.client.get('/admin/users')
        assert resp.status_code == 200
        assert b'Benutzer' in resp.data

    def test_normal_user_gets_403(self):
        login(self.client, 'normal', 'normalpass1')
        resp = self.client.get('/admin/users')
        assert resp.status_code == 403

    def test_anonymous_gets_redirect(self):
        resp = self.client.get('/admin/users')
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_admin_can_create_user(self):
        login(self.client, 'admin', 'adminpass1')
        resp = self.client.post('/admin/users/new', data={
            'username': 'newuser',
            'password': 'newpass12',
            'is_admin': False,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'newuser' in resp.data

    def test_admin_can_deactivate_user(self):
        login(self.client, 'admin', 'adminpass1')
        from models import User
        with self.app.app_context():
            user = User.query.filter_by(username='normal').first()
            user_id = user.id
        # Submit-Button muss immer mitgesendet werden (sonst denkt Flask-WTF: kein Formular)
        # Checkboxen werden weggelassen wenn deaktiviert (kein Wert = False)
        resp = self.client.post('/admin/users/{}/edit'.format(user_id),
                                data={'submit': 'Speichern'},
                                follow_redirects=True)
        assert resp.status_code == 200
        # Verify user is deactivated
        with self.app.app_context():
            user = User.query.filter_by(username='normal').first()
            assert user.is_active_user is False


class TestCreateAdminCLI:
    def test_create_admin_command(self):
        app = create_test_app()
        runner = app.test_cli_runner()
        result = runner.invoke(args=['create-admin', 'cliuser', '--password', 'clipass12'])
        assert 'erstellt' in result.output
        from models import User
        with app.app_context():
            user = User.query.filter_by(username='cliuser').first()
            assert user is not None
            assert user.is_admin is True
