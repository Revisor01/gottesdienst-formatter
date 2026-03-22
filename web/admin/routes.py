from functools import wraps
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from admin import bp
from models import User
from extensions import db
from admin.forms import CreateUserForm, EditUserForm


def admin_required(f):
    """Decorator: login_required + is_admin Check."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=all_users)


@bp.route('/users/new', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Benutzer "{}" angelegt.'.format(user.username), 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', form=form, title='Neuer Benutzer', is_new=True)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    form = EditUserForm(obj=user)
    # is_active Feld auf is_active_user mappen
    if request.method == 'GET':
        form.is_active.data = user.is_active_user
    if form.validate_on_submit():
        if form.password.data:
            user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        user.is_active_user = form.is_active.data
        db.session.commit()
        flash('Benutzer "{}" aktualisiert.'.format(user.username), 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', form=form, user=user, title='Benutzer bearbeiten', is_new=False)
