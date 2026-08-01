from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import Optional, Email, NumberRange, ValidationError


class SettingsForm(FlaskForm):
    smtp_server = StringField('SMTP-Server', validators=[Optional()])
    smtp_port = IntegerField('SMTP-Port', validators=[Optional(), NumberRange(min=1, max=65535)], default=587)
    smtp_username = StringField('SMTP-Benutzername', validators=[Optional()])
    smtp_password = PasswordField('SMTP-Passwort', validators=[Optional()])
    sender_email = StringField('Absender-E-Mail', validators=[Optional(), Email(message='Ungueltige E-Mail-Adresse')])
    recipient_email = StringField('Empfaenger-E-Mail', validators=[Optional(), Email(message='Ungueltige E-Mail-Adresse')])
    send_day = SelectField(
        'Versandtag (Tag des Monats)',
        choices=[(i, str(i)) for i in range(1, 29)],
        coerce=int,
        default=18
    )
    auto_send_enabled = BooleanField('Automatischer Versand aktiviert')
    submit = SubmitField('Speichern')

    def validate(self, extra_validators=None):
        # Standard-Validierung zuerst
        if not super().validate(extra_validators):
            return False

        # Wenn auto_send_enabled, sind smtp_server, sender_email, recipient_email Pflicht
        if self.auto_send_enabled.data:
            errors = False
            if not self.smtp_server.data or not self.smtp_server.data.strip():
                self.smtp_server.errors.append('SMTP-Server ist Pflichtfeld wenn automatischer Versand aktiviert.')
                errors = True
            if not self.sender_email.data or not self.sender_email.data.strip():
                self.sender_email.errors.append('Absender-E-Mail ist Pflichtfeld wenn automatischer Versand aktiviert.')
                errors = True
            if not self.recipient_email.data or not self.recipient_email.data.strip():
                self.recipient_email.errors.append('Empfaenger-E-Mail ist Pflichtfeld wenn automatischer Versand aktiviert.')
                errors = True
            if errors:
                return False

        return True
