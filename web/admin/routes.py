from functools import wraps
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from admin import bp
from models import User, Organization, ServiceTypeMapping, Pastor
from extensions import db
from admin.forms import CreateUserForm, EditUserForm, OrganizationForm, ServiceTypeMappingForm, PastorForm


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


# --- Service Type Mapping CRUD ---

@bp.route('/service-types')
@admin_required
def service_types():
    all_mappings = ServiceTypeMapping.query.order_by(
        ServiceTypeMapping.priority.desc(), ServiceTypeMapping.keyword
    ).all()
    return render_template('admin/service_types.html', mappings=all_mappings)


@bp.route('/service-types/new', methods=['GET', 'POST'])
@admin_required
def create_service_type():
    form = ServiceTypeMappingForm()
    if request.method == 'GET':
        form.is_active.data = True
        form.priority.data = 100
    if form.validate_on_submit():
        keyword = form.keyword.data.strip().lower()
        if ServiceTypeMapping.query.filter_by(keyword=keyword).first():
            flash('Ein Mapping mit diesem Schluesselwort existiert bereits.', 'danger')
            return render_template('admin/edit_service_type.html', form=form, title='Neue Typ-Zuordnung', is_new=True)
        mapping = ServiceTypeMapping(
            keyword=keyword,
            output_label=form.output_label.data.strip(),
            priority=form.priority.data,
            is_active=form.is_active.data,
        )
        db.session.add(mapping)
        db.session.commit()
        _reload_service_types()
        flash('Typ-Zuordnung "{}" angelegt.'.format(mapping.keyword), 'success')
        return redirect(url_for('admin.service_types'))
    return render_template('admin/edit_service_type.html', form=form, title='Neue Typ-Zuordnung', is_new=True)


@bp.route('/service-types/<int:mapping_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_service_type(mapping_id):
    mapping = db.session.get(ServiceTypeMapping, mapping_id)
    if mapping is None:
        abort(404)
    form = ServiceTypeMappingForm(obj=mapping)
    if request.method == 'GET':
        form.keyword.data = mapping.keyword
        form.output_label.data = mapping.output_label
        form.priority.data = mapping.priority
        form.is_active.data = mapping.is_active
    if form.validate_on_submit():
        new_keyword = form.keyword.data.strip().lower()
        existing = ServiceTypeMapping.query.filter_by(keyword=new_keyword).first()
        if existing and existing.id != mapping_id:
            flash('Ein anderes Mapping mit diesem Schluesselwort existiert bereits.', 'danger')
            return render_template('admin/edit_service_type.html', form=form, mapping=mapping, title='Typ-Zuordnung bearbeiten', is_new=False)
        mapping.keyword = new_keyword
        mapping.output_label = form.output_label.data.strip()
        mapping.priority = form.priority.data
        mapping.is_active = form.is_active.data
        db.session.commit()
        _reload_service_types()
        flash('Typ-Zuordnung "{}" aktualisiert.'.format(mapping.keyword), 'success')
        return redirect(url_for('admin.service_types'))
    return render_template('admin/edit_service_type.html', form=form, mapping=mapping, title='Typ-Zuordnung bearbeiten', is_new=False)


@bp.route('/service-types/<int:mapping_id>/delete', methods=['POST'])
@admin_required
def delete_service_type(mapping_id):
    mapping = db.session.get(ServiceTypeMapping, mapping_id)
    if mapping is None:
        abort(404)
    keyword = mapping.keyword
    db.session.delete(mapping)
    db.session.commit()
    _reload_service_types()
    flash('Typ-Zuordnung "{}" geloescht.'.format(keyword), 'success')
    return redirect(url_for('admin.service_types'))


def _reload_service_types():
    """Aktualisiert den Custom-Mappings-Cache nach CRUD-Operationen."""
    from flask import current_app
    from formatting import reload_custom_mappings
    reload_custom_mappings(current_app._get_current_object())


# --- Pastor CRUD ---

@bp.route('/pastors')
@admin_required
def pastors():
    all_pastors = Pastor.query.order_by(Pastor.last_name, Pastor.first_name).all()
    return render_template('admin/pastors.html', pastors=all_pastors)


@bp.route('/pastors/new', methods=['GET', 'POST'])
@admin_required
def create_pastor():
    form = PastorForm()
    if request.method == 'GET':
        form.is_active.data = True
    if form.validate_on_submit():
        pastor = Pastor(
            first_name=form.first_name.data.strip() or None,
            last_name=form.last_name.data.strip(),
            title=form.title.data.strip(),
            is_active=form.is_active.data,
        )
        db.session.add(pastor)
        db.session.commit()
        _reload_pastors()
        flash('Pastor "{}" angelegt.'.format(pastor.last_name), 'success')
        return redirect(url_for('admin.pastors'))
    return render_template('admin/edit_pastor.html', form=form, title='Neuer Pastor', is_new=True)


@bp.route('/pastors/<int:pastor_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_pastor(pastor_id):
    pastor = db.session.get(Pastor, pastor_id)
    if pastor is None:
        abort(404)
    form = PastorForm(obj=pastor)
    if request.method == 'GET':
        form.first_name.data = pastor.first_name or ''
        form.last_name.data = pastor.last_name
        form.title.data = pastor.title
        form.is_active.data = pastor.is_active
    if form.validate_on_submit():
        pastor.first_name = form.first_name.data.strip() or None
        pastor.last_name = form.last_name.data.strip()
        pastor.title = form.title.data.strip()
        pastor.is_active = form.is_active.data
        db.session.commit()
        _reload_pastors()
        flash('Pastor "{}" aktualisiert.'.format(pastor.last_name), 'success')
        return redirect(url_for('admin.pastors'))
    return render_template('admin/edit_pastor.html', form=form, pastor=pastor,
                           title='Pastor bearbeiten', is_new=False)


@bp.route('/pastors/<int:pastor_id>/delete', methods=['POST'])
@admin_required
def delete_pastor(pastor_id):
    pastor = db.session.get(Pastor, pastor_id)
    if pastor is None:
        abort(404)
    last_name = pastor.last_name
    db.session.delete(pastor)
    db.session.commit()
    _reload_pastors()
    flash('Pastor "{}" geloescht.'.format(last_name), 'success')
    return redirect(url_for('admin.pastors'))


def _reload_pastors():
    """Aktualisiert den Pastor-Cache nach CRUD-Operationen."""
    from flask import current_app
    from formatting import reload_pastors
    reload_pastors(current_app._get_current_object())
