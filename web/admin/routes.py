from functools import wraps
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from admin import bp
from models import User, Organization
from extensions import db
from admin.forms import CreateUserForm, EditUserForm, OrganizationForm


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


# --- Organization CRUD ---

@bp.route('/organizations')
@admin_required
def organizations():
    all_orgs = Organization.query.order_by(Organization.id).all()
    return render_template('admin/organizations.html', organizations=all_orgs)


@bp.route('/organizations/new', methods=['GET', 'POST'])
@admin_required
def create_organization():
    form = OrganizationForm()
    form.is_active.data = True if request.method == 'GET' else form.is_active.data
    if form.validate_on_submit():
        if Organization.query.get(form.id.data):
            flash('Eine Organisation mit dieser ID existiert bereits.', 'danger')
            return render_template('admin/edit_organization.html', form=form, title='Neue Organisation', is_new=True)
        org = Organization(
            id=form.id.data,
            name=form.name.data,
            token=form.token.data,
            description=form.description.data or '',
            is_active=form.is_active.data,
        )
        db.session.add(org)
        db.session.commit()
        _reload_orgs()
        flash('Organisation "{}" angelegt.'.format(org.name), 'success')
        return redirect(url_for('admin.organizations'))
    return render_template('admin/edit_organization.html', form=form, title='Neue Organisation', is_new=True)


@bp.route('/organizations/<int:org_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_organization(org_id):
    org = db.session.get(Organization, org_id)
    if org is None:
        abort(404)
    form = OrganizationForm(obj=org)
    if request.method == 'GET':
        form.id.data = org.id
        form.name.data = org.name
        form.token.data = org.token
        form.description.data = org.description
        form.is_active.data = org.is_active
    if form.validate_on_submit():
        org.name = form.name.data
        org.token = form.token.data
        org.description = form.description.data or ''
        org.is_active = form.is_active.data
        db.session.commit()
        _reload_orgs()
        flash('Organisation "{}" aktualisiert.'.format(org.name), 'success')
        return redirect(url_for('admin.organizations'))
    return render_template('admin/edit_organization.html', form=form, org=org, title='Organisation bearbeiten', is_new=False)


@bp.route('/organizations/<int:org_id>/delete', methods=['POST'])
@admin_required
def delete_organization(org_id):
    org = db.session.get(Organization, org_id)
    if org is None:
        abort(404)
    name = org.name
    db.session.delete(org)
    db.session.commit()
    _reload_orgs()
    flash('Organisation "{}" gelöscht.'.format(name), 'success')
    return redirect(url_for('admin.organizations'))


def _reload_orgs():
    """Aktualisiert den Org-Cache nach CRUD-Operationen."""
    from config import reload_organizations
    reload_organizations()
