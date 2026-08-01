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
    return render_template('admin/personen.html', pastors=all_pastors)


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
        flash('Person "{}" angelegt.'.format(pastor.last_name), 'success')
        return redirect(url_for('admin.pastors'))
    return render_template('admin/edit_person.html', form=form, title='Neue Person', is_new=True)


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
        flash('Person "{}" aktualisiert.'.format(pastor.last_name), 'success')
        return redirect(url_for('admin.pastors'))
    return render_template('admin/edit_person.html', form=form, pastor=pastor,
                           title='Person bearbeiten', is_new=False)


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
    flash('Person "{}" geloescht.'.format(last_name), 'success')
    return redirect(url_for('admin.pastors'))


def _reload_pastors():
    """Aktualisiert den Pastor-Cache nach CRUD-Operationen."""
    from flask import current_app
    from formatting import reload_pastors
    reload_pastors(current_app._get_current_object())


# --- Location Rule CRUD (Orts-Mappings / Multi-Kirchen / Nicht-Kirchen) ---

_KIND_LABELS = {
    'mapping': 'Orts-Mapping',
    'multi_church': 'Multi-Kirchen-Ort',
    'non_church': 'Nicht-Kirchen-Stichwort',
}


@bp.route('/location-rules')
@admin_required
def location_rules():
    from models import LocationRule
    rules = LocationRule.query.order_by(LocationRule.kind, LocationRule.key).all()
    grouped = {'mapping': [], 'multi_church': [], 'non_church': []}
    for r in rules:
        grouped.get(r.kind, grouped.setdefault(r.kind, [])).append(r)
    return render_template('admin/location_rules.html', grouped=grouped, kind_labels=_KIND_LABELS)


@bp.route('/location-rules/new', methods=['GET', 'POST'])
@admin_required
def create_location_rule():
    from models import LocationRule
    from admin.forms import LocationRuleForm
    form = LocationRuleForm()
    if request.method == 'GET':
        form.is_active.data = True
        form.kind.data = request.args.get('kind', 'mapping')
    if form.validate_on_submit():
        key = form.key.data.strip().lower()
        kind = form.kind.data
        if LocationRule.query.filter_by(kind=kind, key=key).first():
            flash('Diese Regel existiert bereits.', 'danger')
            return render_template('admin/edit_location_rule.html', form=form, title='Neue Regel', is_new=True)
        rule = LocationRule(
            kind=kind, key=key,
            value=(form.value.data or '').strip() if kind == 'mapping' else '',
            is_active=form.is_active.data,
        )
        db.session.add(rule)
        db.session.commit()
        _reload_location_rules()
        flash('Regel angelegt.', 'success')
        return redirect(url_for('admin.location_rules'))
    return render_template('admin/edit_location_rule.html', form=form, title='Neue Regel', is_new=True)


@bp.route('/location-rules/<int:rule_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_location_rule(rule_id):
    from models import LocationRule
    from admin.forms import LocationRuleForm
    rule = db.session.get(LocationRule, rule_id)
    if rule is None:
        abort(404)
    form = LocationRuleForm(obj=rule)
    if request.method == 'GET':
        form.kind.data = rule.kind
        form.key.data = rule.key
        form.value.data = rule.value
        form.is_active.data = rule.is_active
    if form.validate_on_submit():
        new_key = form.key.data.strip().lower()
        new_kind = form.kind.data
        existing = LocationRule.query.filter_by(kind=new_kind, key=new_key).first()
        if existing and existing.id != rule_id:
            flash('Eine andere Regel mit diesem Schluessel/dieser Art existiert bereits.', 'danger')
            return render_template('admin/edit_location_rule.html', form=form, rule=rule, title='Regel bearbeiten', is_new=False)
        rule.kind = new_kind
        rule.key = new_key
        rule.value = (form.value.data or '').strip() if new_kind == 'mapping' else ''
        rule.is_active = form.is_active.data
        db.session.commit()
        _reload_location_rules()
        flash('Regel aktualisiert.', 'success')
        return redirect(url_for('admin.location_rules'))
    return render_template('admin/edit_location_rule.html', form=form, rule=rule, title='Regel bearbeiten', is_new=False)


@bp.route('/location-rules/<int:rule_id>/delete', methods=['POST'])
@admin_required
def delete_location_rule(rule_id):
    from models import LocationRule
    rule = db.session.get(LocationRule, rule_id)
    if rule is None:
        abort(404)
    db.session.delete(rule)
    db.session.commit()
    _reload_location_rules()
    flash('Regel geloescht.', 'success')
    return redirect(url_for('admin.location_rules'))


def _reload_location_rules():
    """Aktualisiert den Location-Rule-Cache nach CRUD-Operationen."""
    from flask import current_app
    from churchdesk_api import reload_location_rules
    reload_location_rules(current_app._get_current_object())
