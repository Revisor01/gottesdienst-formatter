from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User


class CreateUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8, message='Mindestens 8 Zeichen')])
    is_admin = BooleanField('Admin-Rechte')
    submit = SubmitField('Benutzer anlegen')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Benutzername bereits vergeben.')


class EditUserForm(FlaskForm):
    password = PasswordField('Neues Passwort (leer lassen um nicht zu aendern)')
    is_admin = BooleanField('Admin-Rechte')
    is_active = BooleanField('Aktiv')
    submit = SubmitField('Speichern')

    def validate_password(self, field):
        # Leeres Passwort ist OK (= nicht aendern), aber wenn gesetzt dann min 8
        if field.data and len(field.data) < 8:
            raise ValidationError('Mindestens 8 Zeichen')
