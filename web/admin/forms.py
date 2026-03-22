from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange, Optional
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


class OrganizationForm(FlaskForm):
    id = IntegerField('ChurchDesk Org-ID', validators=[DataRequired(), NumberRange(min=1)])
    name = StringField('Name', validators=[DataRequired(), Length(max=256)])
    token = StringField('API-Token', validators=[DataRequired()])
    description = TextAreaField('Beschreibung', validators=[Optional(), Length(max=1024)])
    is_active = BooleanField('Aktiv')
    submit = SubmitField('Speichern')


class ServiceTypeMappingForm(FlaskForm):
    keyword = StringField('Schluesselwort (Kleinschreibung)', validators=[DataRequired(), Length(max=256)])
    output_label = StringField('Ausgabe-Bezeichnung', validators=[DataRequired(), Length(max=256)])
    priority = IntegerField('Prioritaet', validators=[NumberRange(min=0)], default=100)
    is_active = BooleanField('Aktiv')
    submit = SubmitField('Speichern')
