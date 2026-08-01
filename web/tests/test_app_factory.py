#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-Tests fuer App-Factory-Refactor und User-Modell.
"""
import os
import pytest

# SECRET_KEY fuer Tests setzen
os.environ['SECRET_KEY'] = 'test-secret-key-for-unit-tests'


def create_test_app():
    """Test-App mit temporaerer SQLite-DB."""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # In-Memory
    app.config['WTF_CSRF_ENABLED'] = False
    from extensions import db
    with app.app_context():
        db.create_all()
    return app


class TestAppFactory:
    def test_create_app_returns_flask_instance(self):
        app = create_test_app()
        assert app is not None
        assert app.config['TESTING'] is True

    def test_secret_key_required(self):
        old = os.environ.pop('SECRET_KEY', None)
        try:
            from app import create_app
            with pytest.raises(RuntimeError, match='SECRET_KEY'):
                create_app()
        finally:
            if old:
                os.environ['SECRET_KEY'] = old

    def test_index_route_redirects_without_login(self):
        app = create_test_app()
        with app.test_client() as client:
            resp = client.get('/')
            # Alle Routes ausser /login und /health erfordern Login
            assert resp.status_code == 302
            assert '/login' in resp.headers['Location']

    def test_routes_use_main_blueprint(self):
        app = create_test_app()
        rules = [r.endpoint for r in app.url_map.iter_rules()]
        assert 'main.index' in rules
        assert 'main.download_file' in rules
        assert 'main.fetch_churchdesk_events' in rules
        assert 'main.export_selected_events' in rules


class TestUserModel:
    def test_set_and_check_password(self):
        from models import User
        user = User(username='test')
        user.set_password('geheim123')
        assert user.check_password('geheim123')
        assert not user.check_password('falsch')

    def test_is_active_reflects_is_active_user(self):
        from models import User
        user = User(username='test', is_active_user=True)
        assert user.is_active is True
        user.is_active_user = False
        assert user.is_active is False
