#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gottesdienst-Formatter Web Interface — App Factory.
Pastor Simon Luthe - Kirchenkreis Dithmarschen
"""
import os
from flask import Flask


def create_app():
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

    return app


# Fuer lokale Entwicklung: SECRET_KEY=dev python app.py
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
