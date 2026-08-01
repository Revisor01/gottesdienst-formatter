#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login/Logout-Routes fuer den Auth Blueprint.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from auth import bp
from models import User
from auth.forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Falscher Benutzername oder Passwort', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Sicherheit: nur relative URLs akzeptieren
        if next_page and not next_page.startswith('/'):
            next_page = None
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Erfolgreich abgemeldet.', 'info')
    return redirect(url_for('auth.login'))
