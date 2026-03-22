#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gottesdienst-Formatter Web Interface — App Factory.
Pastor Simon Luthe - Kirchenkreis Dithmarschen
"""
import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)

    # SECRET_KEY — MUSS gesetzt sein, kein Fallback (Pitfall 1)
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError(
            'SECRET_KEY nicht gesetzt. '
            'Generiere mit: python -c "import secrets; print(secrets.token_hex(32))" '
            'und setze als Environment Variable.'
        )
    app.config['SECRET_KEY'] = secret_key

    # Datenbank — SQLite in /app/data/ (Docker Volume)
    db_path = os.path.join(app.root_path, 'data', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Test-Konfiguration ueberschreibt Defaults (muss vor db.init_app gesetzt werden)
    if test_config is not None:
        app.config.update(test_config)

    # Session-Konfiguration (30-Tage Remember Me)
    app.config['REMEMBER_COOKIE_DURATION'] = 30 * 24 * 3600  # 30 Tage in Sekunden

    # Extensions initialisieren
    from extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User-Loader fuer Flask-Login
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints registrieren
    from main import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from settings import bp as settings_bp
    app.register_blueprint(settings_bp)

    import click

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.password_option()
    def create_admin_command(username, password):
        """Erstellt einen Admin-Benutzer."""
        from models import User
        if User.query.filter_by(username=username).first():
            click.echo('Fehler: Benutzer "{}" existiert bereits.'.format(username))
            raise SystemExit(1)
        if len(password) < 8:
            click.echo('Fehler: Passwort muss mindestens 8 Zeichen haben.')
            raise SystemExit(1)
        user = User(username=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('Admin-Benutzer "{}" erstellt.'.format(username))

    return app


# Fuer lokale Entwicklung: SECRET_KEY=dev python app.py
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
