#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mail-Service fuer automatischen Boyens-Export.

Stellt bereit:
  - generate_next_month_export() → str
  - send_boyens_mail(user_settings, export_text, secret_key) → (bool, str)
  - get_effective_send_date(year, month, day) → datetime.date
"""
import smtplib
import socket
import logging
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import ORGANIZATIONS
from churchdesk_api import EventAnalyzer, create_multi_org_client
from crypto import decrypt_value

logger = logging.getLogger(__name__)


def get_effective_send_date(year: int, month: int, day: int) -> datetime.date:
    """Berechnet den effektiven Versandtag unter Beruecksichtigung der Wochenend-Logik.

    Samstag (weekday 5) → 1 Tag zurueck (Freitag).
    Sonntag  (weekday 6) → 2 Tage zurueck (Freitag).

    Args:
        year:  Jahr
        month: Monat (1-12)
        day:   Geplanter Versandtag (1-28)

    Returns:
        datetime.date — tatsaechlicher Versandtag
    """
    import calendar
    # Auf letzten Tag des Monats begrenzen (Constraint 1-28 sollte das nie treffen,
    # aber sicherheitshalber)
    max_day = calendar.monthrange(year, month)[1]
    day = min(day, max_day)

    send_date = datetime.date(year, month, day)

    if send_date.weekday() == 5:   # Samstag
        send_date -= datetime.timedelta(days=1)
    elif send_date.weekday() == 6:  # Sonntag
        send_date -= datetime.timedelta(days=2)

    return send_date


def generate_next_month_export() -> str:
    """Generiert den Boyens-Export fuer den Folgemonat.

    Berechnet automatisch Jahr/Monat des Folgemonats (Dezember → Januar naechstes Jahr).
    Nutzt alle konfigurierten ORGANIZATIONS.

    Returns:
        Formatierter Boyens-Text als String.
        Leerer String wenn keine Events gefunden oder ORGANIZATIONS leer.
    """
    # Folgemonat berechnen
    today = datetime.date.today()
    if today.month == 12:
        target_year = today.year + 1
        target_month = 1
    else:
        target_year = today.year
        target_month = today.month + 1

    logger.info('generate_next_month_export: Lade Events fuer %d/%d', target_month, target_year)

    if not ORGANIZATIONS:
        logger.warning('generate_next_month_export: Keine ORGANIZATIONS konfiguriert')
        return ''

    try:
        org_ids = list(ORGANIZATIONS.keys())
        client = create_multi_org_client(org_ids)
        events = client.get_monthly_events(target_year, target_month, gottesdienst_only=True)
    except Exception as e:
        logger.error('generate_next_month_export: API-Fehler: %s', str(e))
        raise

    if not events:
        logger.info('generate_next_month_export: Keine Events gefunden')
        return ''

    # Events durch EventAnalyzer formatieren (wie in main/routes.py)
    processed_events = []
    for event in events:
        formatted = EventAnalyzer.format_event_for_boyens(event)
        if formatted:
            formatted['organization_name'] = event.get('organization_name', '')
            processed_events.append(formatted)

    if not processed_events:
        logger.info('generate_next_month_export: Keine verarbeitbaren Events')
        return ''

    # In Boyens-Format konvertieren — lokaler Import um Circular-Imports zu vermeiden
    from main.routes import convert_churchdesk_events_to_boyens

    # convert_churchdesk_events_to_boyens erwartet Dicts mit isoformat startDate
    events_for_conversion = []
    for ev in processed_events:
        events_for_conversion.append({
            'id': ev['id'],
            'title': ev['title'],
            'startDate': ev['startDate'].isoformat(),
            'location': ev['location'],
            'contributor': ev['contributor'],
            'parishes': ev['parishes'],
            'organization_name': ev.get('organization_name', ''),
        })

    export_text = convert_churchdesk_events_to_boyens(events_for_conversion)
    logger.info('generate_next_month_export: Export erfolgreich (%d Zeichen)', len(export_text))
    return export_text


def send_boyens_mail(user_settings, export_text: str, secret_key: str) -> tuple:
    """Verschickt den Boyens-Export per Mail an den konfigurierten Empfaenger.

    Args:
        user_settings:  UserSettings-Objekt mit SMTP-Konfiguration.
        export_text:    Formatierter Boyens-Text.
        secret_key:     SECRET_KEY fuer SMTP-Passwort-Entschluesselung.

    Returns:
        (True, 'Erfolgreich gesendet') oder (False, 'Fehler: ...')
    """
    # Folgemonat fuer Betreff / Dateiname berechnen
    today = datetime.date.today()
    if today.month == 12:
        mail_year = today.year + 1
        mail_month = 1
    else:
        mail_year = today.year
        mail_month = today.month + 1

    month_names = {
        1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
        5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
    }
    month_name = month_names[mail_month]

    subject = 'Gottesdienste {} {} — Boyens-Export'.format(month_name, mail_year)
    filename = 'gottesdienste_{}_{}.txt'.format(
        month_name.lower().replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe'),
        mail_year
    )

    try:
        password = decrypt_value(user_settings.smtp_password_encrypted, secret_key)
    except Exception as e:
        return False, 'Fehler beim Entschluesseln des SMTP-Passworts: {}'.format(str(e))

    # E-Mail aufbauen
    msg = MIMEMultipart('mixed')
    msg['From'] = user_settings.sender_email
    msg['To'] = user_settings.recipient_email
    msg['Subject'] = subject

    # Body: formatierter Text direkt
    body_part = MIMEText(export_text, 'plain', 'utf-8')
    msg.attach(body_part)

    # Anhang: gleicher Text als .txt-Datei
    attachment = MIMEText(export_text, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)

    try:
        with smtplib.SMTP(user_settings.smtp_server, user_settings.smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user_settings.smtp_username, password)
            server.send_message(msg)
        logger.info('send_boyens_mail: Mail erfolgreich gesendet an %s', user_settings.recipient_email)
        return True, 'Erfolgreich gesendet'

    except smtplib.SMTPAuthenticationError as e:
        msg_err = 'SMTP-Authentifizierung fehlgeschlagen: {}'.format(str(e))
        logger.error('send_boyens_mail: %s', msg_err)
        return False, msg_err

    except smtplib.SMTPException as e:
        msg_err = 'SMTP-Fehler: {}'.format(str(e))
        logger.error('send_boyens_mail: %s', msg_err)
        return False, msg_err

    except socket.timeout:
        msg_err = 'Verbindung zum SMTP-Server abgelaufen'
        logger.error('send_boyens_mail: %s', msg_err)
        return False, msg_err

    except Exception as e:
        msg_err = 'Fehler beim Mail-Versand: {}'.format(str(e))
        logger.error('send_boyens_mail: %s', msg_err)
        return False, msg_err
