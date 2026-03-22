import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user

from settings import bp
from models import UserSettings
from extensions import db
from crypto import encrypt_value, decrypt_value
from settings.forms import SettingsForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def settings_page():
    """GET/POST /settings — SMTP-Einstellungen laden und speichern."""
    from config import ORGANIZATIONS

    # UserSettings fuer aktuellen User laden oder neu anlegen
    user_settings = current_user.settings
    if user_settings is None:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.flush()

    form = SettingsForm()

    if request.method == 'GET':
        # Formular mit bestehenden Werten vorausfuellen (Passwort NICHT)
        form.smtp_server.data = user_settings.smtp_server or ''
        form.smtp_port.data = user_settings.smtp_port or 587
        form.smtp_username.data = user_settings.smtp_username or ''
        form.sender_email.data = user_settings.sender_email or ''
        form.recipient_email.data = user_settings.recipient_email or ''
        form.send_day.data = user_settings.send_day or 18
        form.auto_send_enabled.data = user_settings.auto_send_enabled or False
        # smtp_password intentionally left empty

    elif form.validate_on_submit():
        user_settings.smtp_server = form.smtp_server.data or ''
        user_settings.smtp_port = form.smtp_port.data or 587
        user_settings.smtp_username = form.smtp_username.data or ''
        user_settings.sender_email = form.sender_email.data or ''
        user_settings.recipient_email = form.recipient_email.data or ''
        user_settings.send_day = form.send_day.data
        user_settings.auto_send_enabled = form.auto_send_enabled.data

        # Passwort nur speichern wenn neu eingegeben
        if form.smtp_password.data:
            secret_key = current_app.config['SECRET_KEY']
            user_settings.smtp_password_encrypted = encrypt_value(form.smtp_password.data, secret_key)

        db.session.commit()
        flash('Einstellungen gespeichert.', 'success')
        return redirect(url_for('settings.settings_page'))

    return render_template(
        'settings/settings.html',
        form=form,
        organizations=ORGANIZATIONS,
        settings=user_settings,
        has_password=bool(user_settings.smtp_password_encrypted)
    )


@bp.route('/test-mail', methods=['POST'])
@login_required
def test_mail():
    """POST /settings/test-mail — Sendet Test-Mail via smtplib, gibt JSON zurueck."""
    user_settings = current_user.settings

    if not user_settings:
        return jsonify({'success': False, 'message': 'Keine SMTP-Einstellungen konfiguriert.'})

    if not user_settings.smtp_server:
        return jsonify({'success': False, 'message': 'SMTP-Server nicht konfiguriert.'})

    if not user_settings.sender_email:
        return jsonify({'success': False, 'message': 'Absender-E-Mail nicht konfiguriert.'})

    if not user_settings.recipient_email:
        return jsonify({'success': False, 'message': 'Empfaenger-E-Mail nicht konfiguriert.'})

    if not user_settings.smtp_password_encrypted:
        return jsonify({'success': False, 'message': 'SMTP-Passwort nicht konfiguriert.'})

    try:
        secret_key = current_app.config['SECRET_KEY']
        password = decrypt_value(user_settings.smtp_password_encrypted, secret_key)

        msg = MIMEMultipart()
        msg['From'] = user_settings.sender_email
        msg['To'] = user_settings.recipient_email
        msg['Subject'] = 'Test-Mail vom Gottesdienst-Formatter'

        body = 'Diese Test-Mail bestaetigt, dass Ihre SMTP-Einstellungen korrekt konfiguriert sind.'
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP(user_settings.smtp_server, user_settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(user_settings.smtp_username, password)
            server.sendmail(user_settings.sender_email, user_settings.recipient_email, msg.as_string())

        return jsonify({'success': True, 'message': 'Test-Mail erfolgreich gesendet!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
