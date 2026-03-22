#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APScheduler-Integration fuer automatischen monatlichen Boyens-Mail-Versand.

Taeglicher Job um 8:00 Uhr prueft welche User heute eine Mail bekommen sollen.
Wochenend-Logik: Sa/So wird auf den vorherigen Freitag verschoben.
Retry: 1x nach 1 Stunde bei Fehler.
"""
import os
import logging
import datetime
import atexit
from datetime import timezone, timedelta

logger = logging.getLogger(__name__)


def init_scheduler(app):
    """Initialisiert den APScheduler und registriert den taeglichen Mail-Check.

    Wird NICHT gestartet wenn:
    - app.config['TESTING'] ist True
    - Werkzeug-Reloader Unter-Prozess (WERKZEUG_RUN_MAIN == 'false')

    Args:
        app: Flask-App-Instanz (wird an Jobs weitergegeben fuer app_context)
    """
    if app.config.get('TESTING'):
        logger.debug('init_scheduler: TESTING=True — Scheduler nicht gestartet')
        return

    # Im Werkzeug-Reloader-Modus nur im Main-Prozess starten
    # WERKZEUG_RUN_MAIN ist 'true' im Reloader-Child-Prozess,
    # nicht gesetzt in Gunicorn/Produktion (dort direkt starten)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'false':
        logger.debug('init_scheduler: Werkzeug Reloader-Prozess — Scheduler nicht gestartet')
        return

    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        check_and_send_mails,
        CronTrigger(hour=8, minute=0),
        args=[app],
        id='daily_mail_check',
        replace_existing=True,
        misfire_grace_time=3600  # 1 Stunde Toleranz bei verpasstem Ausfuehrungszeitpunkt
    )

    scheduler.start()
    app._scheduler = scheduler

    def _shutdown_scheduler():
        try:
            scheduler.shutdown(wait=False)
        except Exception:
            pass

    atexit.register(_shutdown_scheduler)
    logger.info('init_scheduler: APScheduler gestartet — taeglicher Check um 08:00 Uhr')


def check_and_send_mails(app):
    """Taeglicher Job: Prueft welche User heute eine Mail bekommen und verschickt sie.

    Logik:
    1. Alle UserSettings mit auto_send_enabled=True und smtp_server laden.
    2. Fuer jeden User effective_date berechnen.
    3. Wenn effective_date == heute UND nicht bereits in diesem Monat gesendet:
       Export generieren und Mail schicken.
    4. Bei Fehler: Retry nach 1 Stunde einplanen.
    """
    from extensions import db
    from models import UserSettings
    from mail_service import generate_next_month_export, send_boyens_mail, get_effective_send_date

    with app.app_context():
        today = datetime.date.today()
        logger.info('check_and_send_mails: Pruefe Mail-Versand fuer %s', today)

        # Alle User mit aktiviertem Auto-Versand und konfiguriertem SMTP-Server
        users_settings = UserSettings.query.filter_by(auto_send_enabled=True).filter(
            UserSettings.smtp_server != '',
            UserSettings.smtp_server.isnot(None)
        ).all()

        logger.info('check_and_send_mails: %d User mit auto_send_enabled', len(users_settings))

        for settings in users_settings:
            try:
                _process_user_mail(app, settings, today)
            except Exception as e:
                logger.error(
                    'check_and_send_mails: Unbehandelter Fehler fuer user_id=%d: %s',
                    settings.user_id, str(e)
                )
                try:
                    db.session.rollback()
                except Exception:
                    pass


def _process_user_mail(app, settings, today):
    """Verarbeitet einen einzelnen User — Kernlogik des taeglichen Checks."""
    from extensions import db
    from mail_service import generate_next_month_export, send_boyens_mail, get_effective_send_date

    effective_date = get_effective_send_date(today.year, today.month, settings.send_day)

    if effective_date != today:
        logger.debug(
            '_process_user_mail: user_id=%d — kein Versandtag heute '
            '(send_day=%d, effective=%s, today=%s)',
            settings.user_id, settings.send_day, effective_date, today
        )
        return

    # Bereits diesen Monat gesendet? (last_send_date im selben Jahr+Monat)
    if settings.last_send_date is not None:
        last = settings.last_send_date
        if last.year == today.year and last.month == today.month:
            logger.info(
                '_process_user_mail: user_id=%d — bereits gesendet am %s, skip',
                settings.user_id, last.date()
            )
            return

    logger.info('_process_user_mail: user_id=%d — Versandtag erreicht, generiere Export', settings.user_id)

    try:
        export_text = generate_next_month_export()
    except Exception as e:
        logger.error('_process_user_mail: Export-Generierung fehlgeschlagen: %s', str(e))
        settings.last_send_status = 'Export-Fehler: {}'.format(str(e))
        db.session.commit()
        return

    if not export_text:
        logger.info('_process_user_mail: user_id=%d — Export leer, kein Versand', settings.user_id)
        settings.last_send_status = 'Keine Events fuer naechsten Monat'
        db.session.commit()
        return

    success, message = send_boyens_mail(settings, export_text, app.config['SECRET_KEY'])

    if success:
        settings.last_send_date = datetime.datetime.now(timezone.utc)
        settings.last_send_status = message
        db.session.commit()
        logger.info('_process_user_mail: user_id=%d — Mail erfolgreich gesendet', settings.user_id)
    else:
        logger.warning(
            '_process_user_mail: user_id=%d — Versand fehlgeschlagen: %s — Retry in 1h',
            settings.user_id, message
        )
        # Retry nach 1 Stunde einplanen
        if hasattr(app, '_scheduler'):
            retry_time = datetime.datetime.now() + timedelta(hours=1)
            app._scheduler.add_job(
                retry_send_mail,
                'date',
                run_date=retry_time,
                args=[app, settings.id, export_text],
                id='retry_mail_{}'.format(settings.user_id),
                replace_existing=True
            )
            logger.info(
                '_process_user_mail: user_id=%d — Retry eingeplant fuer %s',
                settings.user_id, retry_time
            )


def retry_send_mail(app, settings_id: int, export_text: str):
    """Einmaliger Retry-Job nach 1 Stunde bei fehlgeschlagenem Erstversand.

    Setzt last_send_date auch bei Fehler (markiert als "versucht").
    """
    from extensions import db
    from models import UserSettings
    from mail_service import send_boyens_mail

    with app.app_context():
        settings = db.session.get(UserSettings, settings_id)
        if settings is None:
            logger.error('retry_send_mail: UserSettings id=%d nicht gefunden', settings_id)
            return

        logger.info('retry_send_mail: Retry fuer user_id=%d', settings.user_id)
        success, message = send_boyens_mail(settings, export_text, app.config['SECRET_KEY'])

        # Auch bei Fehler last_send_date setzen — markiert als "versucht"
        settings.last_send_date = datetime.datetime.now(timezone.utc)

        if success:
            settings.last_send_status = message
            logger.info('retry_send_mail: user_id=%d — Retry erfolgreich', settings.user_id)
        else:
            settings.last_send_status = 'Fehlgeschlagen nach Retry: {}'.format(message)
            logger.error(
                'retry_send_mail: user_id=%d — Retry fehlgeschlagen: %s',
                settings.user_id, message
            )

        db.session.commit()
