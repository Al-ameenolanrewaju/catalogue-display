from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models import (
    AdminUser, WebsiteCategory, WebsiteProject, WebsiteImage, 
    ProjectFeature, Package, PackageFeature, AddOn, 
    Enquiry, EnquiryNote, EnquiryStatus, SiteSetting
)
from app.blueprints.admin.forms import (
    LoginForm, CategoryForm, WebsiteProjectForm, 
    PackageForm, AddOnForm, EnquiryStatusForm, 
    EnquiryNoteForm, SiteSettingsForm
)
from app.services.analytics_service import get_dashboard_metrics
from app.services.storage import save_image_file
from app.services.whatsapp import clean_phone_number

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip()
        user = AdminUser.query.filter(
            or_(AdminUser.username == identity, AdminUser.email == identity)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    metrics = get_dashboard_metrics()
    recent_enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).limit(8).all()
    recent_projects = WebsiteProject.query.order_by(WebsiteProject.created_at.desc()).limit(5).all()
    return render_template(
        'admin/dashboard.html',
        metrics=metrics,
        recent_enquiries=recent_enquiries,
        recent_projects=recent_projects
    )


# ==========================================
# WEBSITES MANAGEMENT
# ==========================================

@admin_bp.route('/websites')
@login_required
def websites_list():
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('q', '').strip()

    query = WebsiteProject.query
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search:
        query = query.filter(
            or_(
                WebsiteProject.title.ilike(f'%{search}%'),
                WebsiteProject.intended_business_type.ilike(f'%{search}%')
            )
        )

    projects = query.order_by(WebsiteProject.created_at.desc()).all()
    categories = WebsiteCategory.query.order_by(WebsiteCategory.name).all()
    return render_template('admin/websites/index.html', projects=projects, categories=categories, current_filter=status, current_search=search)


@admin_bp.route('/websites/new', methods=['GET', 'POST'])
@login_required
def website_create():
    form = WebsiteProjectForm()
    categories = WebsiteCategory.query.filter_by(is_active=True).order_by(WebsiteCategory.name).all()
    form.category_id.choices = [(0, '-- None / Uncategorized --')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        base_slug = WebsiteProject.generate_slug(form.title.data)
        slug = base_slug
        count = 1
        while WebsiteProject.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{count}"
            count += 1

        cat_id = form.category_id.data if form.category_id.data != 0 else None

        project = WebsiteProject(
            title=form.title.data.strip(),
            slug=slug,
            category_id=cat_id,
            intended_business_type=form.intended_business_type.data.strip(),
            short_description=form.short_description.data.strip(),
            full_description=form.full_description.data.strip(),
            live_demo_url=form.live_demo_url.data.strip() if form.live_demo_url.data else None,
            is_featured=form.is_featured.data,
            is_published=form.is_published.data
        )
        db.session.add(project)
        db.session.flush()

        # Handle features
        if form.features.data:
            lines = [line.strip() for line in form.features.data.splitlines() if line.strip()]
            for order, text in enumerate(lines):
                feat = ProjectFeature(project_id=project.id, feature_text=text, display_order=order)
                db.session.add(feat)

        # Primary image: file or URL
        primary_url = None
        if form.primary_image_file.data:
            try:
                primary_url = save_image_file(form.primary_image_file.data, folder='projects')
            except Exception as e:
                flash(f'Error uploading primary image: {str(e)}', 'warning')
        elif form.primary_image_url.data:
            primary_url = form.primary_image_url.data.strip()

        if primary_url:
            img = WebsiteImage(project_id=project.id, image_url=primary_url, is_primary=True, display_order=0)
            db.session.add(img)

        # Additional gallery images
        if form.gallery_image_urls.data:
            gallery_lines = [line.strip() for line in form.gallery_image_urls.data.splitlines() if line.strip()]
            for order, g_url in enumerate(gallery_lines, start=1):
                g_img = WebsiteImage(project_id=project.id, image_url=g_url, is_primary=False, display_order=order)
                db.session.add(g_img)

        db.session.commit()
        flash(f'Website project "{project.title}" created successfully.', 'success')
        return redirect(url_for('admin.websites_list'))

    return render_template('admin/websites/form.html', form=form, title='Add New Website Showcase', project=None)


@admin_bp.route('/websites/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def website_edit(project_id):
    project = db.get_or_404(WebsiteProject, project_id)
    form = WebsiteProjectForm()
    categories = WebsiteCategory.query.filter_by(is_active=True).order_by(WebsiteCategory.name).all()
    form.category_id.choices = [(0, '-- None / Uncategorized --')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        project.title = form.title.data.strip()
        project.category_id = form.category_id.data if form.category_id.data != 0 else None
        project.intended_business_type = form.intended_business_type.data.strip()
        project.short_description = form.short_description.data.strip()
        project.full_description = form.full_description.data.strip()
        project.live_demo_url = form.live_demo_url.data.strip() if form.live_demo_url.data else None
        project.is_featured = form.is_featured.data
        project.is_published = form.is_published.data

        # Update features
        ProjectFeature.query.filter_by(project_id=project.id).delete()
        if form.features.data:
            lines = [line.strip() for line in form.features.data.splitlines() if line.strip()]
            for order, text in enumerate(lines):
                feat = ProjectFeature(project_id=project.id, feature_text=text, display_order=order)
                db.session.add(feat)

        # Upload new primary image if provided
        new_primary_url = None
        if form.primary_image_file.data:
            try:
                new_primary_url = save_image_file(form.primary_image_file.data, folder='projects')
            except Exception as e:
                flash(f'Error uploading primary image: {str(e)}', 'warning')
        elif form.primary_image_url.data:
            new_primary_url = form.primary_image_url.data.strip()

        if new_primary_url:
            existing_primary = WebsiteImage.query.filter_by(project_id=project.id, is_primary=True).first()
            if existing_primary:
                existing_primary.image_url = new_primary_url
            else:
                db.session.add(WebsiteImage(project_id=project.id, image_url=new_primary_url, is_primary=True, display_order=0))

        # Additional gallery images
        if form.gallery_image_urls.data:
            # Keep primary, replace secondary gallery
            WebsiteImage.query.filter_by(project_id=project.id, is_primary=False).delete()
            gallery_lines = [line.strip() for line in form.gallery_image_urls.data.splitlines() if line.strip()]
            for order, g_url in enumerate(gallery_lines, start=1):
                g_img = WebsiteImage(project_id=project.id, image_url=g_url, is_primary=False, display_order=order)
                db.session.add(g_img)

        db.session.commit()
        flash(f'Website project "{project.title}" updated successfully.', 'success')
        return redirect(url_for('admin.websites_list'))

    elif request.method == 'GET':
        form.title.data = project.title
        form.category_id.data = project.category_id or 0
        form.intended_business_type.data = project.intended_business_type
        form.short_description.data = project.short_description
        form.full_description.data = project.full_description
        form.live_demo_url.data = project.live_demo_url
        form.is_featured.data = project.is_featured
        form.is_published.data = project.is_published
        form.features.data = "\n".join([f.feature_text for f in project.features])
        primary = project.primary_image
        form.primary_image_url.data = primary.image_url if primary else ""
        gallery_images = [img.image_url for img in project.images if not img.is_primary]
        form.gallery_image_urls.data = "\n".join(gallery_images)

    return render_template('admin/websites/form.html', form=form, title='Edit Website Showcase', project=project)


@admin_bp.route('/websites/<int:project_id>/delete', methods=['POST'])
@login_required
def website_delete(project_id):
    project = db.get_or_404(WebsiteProject, project_id)
    title = project.title
    db.session.delete(project)
    db.session.commit()
    flash(f'Website "{title}" has been deleted.', 'info')
    return redirect(url_for('admin.websites_list'))


@admin_bp.route('/websites/<int:project_id>/toggle-status', methods=['POST'])
@login_required
def website_toggle_status(project_id):
    project = db.get_or_404(WebsiteProject, project_id)
    project.is_published = not project.is_published
    db.session.commit()
    status_label = 'published' if project.is_published else 'saved as draft'
    flash(f'Project "{project.title}" is now {status_label}.', 'success')
    return redirect(request.referrer or url_for('admin.websites_list'))


# ==========================================
# CATEGORIES MANAGEMENT
# ==========================================

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories_index():
    form = CategoryForm()
    if form.validate_on_submit():
        base_slug = WebsiteCategory.generate_slug(form.name.data)
        slug = base_slug
        count = 1
        while WebsiteCategory.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{count}"
            count += 1

        cat = WebsiteCategory(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data.strip() if form.description.data else None,
            display_order=form.display_order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{cat.name}" added successfully.', 'success')
        return redirect(url_for('admin.categories_index'))

    categories = WebsiteCategory.query.order_by(WebsiteCategory.display_order.asc(), WebsiteCategory.name.asc()).all()
    return render_template('admin/categories/index.html', categories=categories, form=form)


@admin_bp.route('/categories/<int:cat_id>/edit', methods=['POST'])
@login_required
def category_edit(cat_id):
    cat = db.get_or_404(WebsiteCategory, cat_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    display_order = request.form.get('display_order', 0, type=int)
    is_active = bool(request.form.get('is_active'))

    if name:
        cat.name = name
        cat.description = description
        cat.display_order = display_order
        cat.is_active = is_active
        db.session.commit()
        flash(f'Category "{cat.name}" updated successfully.', 'success')
    else:
        flash('Category name cannot be empty.', 'danger')
    return redirect(url_for('admin.categories_index'))


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
def category_delete(cat_id):
    cat = db.get_or_404(WebsiteCategory, cat_id)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{name}" removed.', 'info')
    return redirect(url_for('admin.categories_index'))


# ==========================================
# PACKAGES MANAGEMENT
# ==========================================

@admin_bp.route('/packages')
@login_required
def packages_list():
    packages = Package.query.order_by(Package.display_order.asc()).all()
    return render_template('admin/packages/index.html', packages=packages)


@admin_bp.route('/packages/new', methods=['GET', 'POST'])
@login_required
def package_create():
    form = PackageForm()
    if form.validate_on_submit():
        pkg = Package(
            name=form.name.data.strip(),
            slug=form.slug.data.strip().lower(),
            description=form.description.data.strip(),
            price=float(form.price.data) if form.price.data is not None else None,
            is_recommended=form.is_recommended.data,
            display_order=form.display_order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(pkg)
        db.session.flush()

        if form.features.data:
            lines = [l.strip() for l in form.features.data.splitlines() if l.strip()]
            for order, line in enumerate(lines):
                is_inc = not line.startswith('-')
                text = line.lstrip('-').strip()
                pf = PackageFeature(package_id=pkg.id, feature_text=text, is_included=is_inc, display_order=order)
                db.session.add(pf)

        db.session.commit()
        flash(f'Package "{pkg.name}" created successfully.', 'success')
        return redirect(url_for('admin.packages_list'))

    return render_template('admin/packages/form.html', form=form, title='Create Package', package=None)


@admin_bp.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
def package_edit(package_id):
    pkg = db.get_or_404(Package, package_id)
    form = PackageForm()

    if form.validate_on_submit():
        pkg.name = form.name.data.strip()
        pkg.slug = form.slug.data.strip().lower()
        pkg.description = form.description.data.strip()
        pkg.price = float(form.price.data) if form.price.data is not None else None
        pkg.is_recommended = form.is_recommended.data
        pkg.display_order = form.display_order.data or 0
        pkg.is_active = form.is_active.data

        PackageFeature.query.filter_by(package_id=pkg.id).delete()
        if form.features.data:
            lines = [l.strip() for l in form.features.data.splitlines() if l.strip()]
            for order, line in enumerate(lines):
                is_inc = not line.startswith('-')
                text = line.lstrip('-').strip()
                pf = PackageFeature(package_id=pkg.id, feature_text=text, is_included=is_inc, display_order=order)
                db.session.add(pf)

        db.session.commit()
        flash(f'Package "{pkg.name}" updated successfully.', 'success')
        return redirect(url_for('admin.packages_list'))

    elif request.method == 'GET':
        form.name.data = pkg.name
        form.slug.data = pkg.slug
        form.description.data = pkg.description
        form.price.data = pkg.price
        form.is_recommended.data = pkg.is_recommended
        form.display_order.data = pkg.display_order
        form.is_active.data = pkg.is_active
        lines = []
        for feat in pkg.features:
            prefix = '' if feat.is_included else '-'
            lines.append(f"{prefix}{feat.feature_text}")
        form.features.data = "\n".join(lines)

    return render_template('admin/packages/form.html', form=form, title='Edit Package', package=pkg)


@admin_bp.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
def package_delete(package_id):
    pkg = db.get_or_404(Package, package_id)
    name = pkg.name
    db.session.delete(pkg)
    db.session.commit()
    flash(f'Package "{name}" removed.', 'info')
    return redirect(url_for('admin.packages_list'))


# ==========================================
# ADD-ONS MANAGEMENT
# ==========================================

@admin_bp.route('/add-ons', methods=['GET', 'POST'])
@login_required
def addons_index():
    form = AddOnForm()
    if form.validate_on_submit():
        price = float(form.price.data) if form.price.data is not None else None
        addon = AddOn(
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            price=price,
            display_order=form.display_order.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(addon)
        db.session.commit()
        flash(f'Add-on "{addon.name}" created successfully.', 'success')
        return redirect(url_for('admin.addons_index'))

    addons = AddOn.query.order_by(AddOn.display_order.asc(), AddOn.name.asc()).all()
    return render_template('admin/addons/index.html', addons=addons, form=form)


@admin_bp.route('/add-ons/<int:addon_id>/edit', methods=['POST'])
@login_required
def addon_edit(addon_id):
    addon = db.get_or_404(AddOn, addon_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price_val = request.form.get('price', '').strip()
    price = float(price_val) if price_val else None
    display_order = request.form.get('display_order', 0, type=int)
    is_active = bool(request.form.get('is_active'))

    if name and description:
        addon.name = name
        addon.description = description
        addon.price = price
        addon.display_order = display_order
        addon.is_active = is_active
        db.session.commit()
        flash(f'Add-on "{addon.name}" updated.', 'success')
    else:
        flash('Add-on name and description are required.', 'danger')
    return redirect(url_for('admin.addons_index'))


@admin_bp.route('/add-ons/<int:addon_id>/delete', methods=['POST'])
@login_required
def addon_delete(addon_id):
    addon = db.get_or_404(AddOn, addon_id)
    name = addon.name
    db.session.delete(addon)
    db.session.commit()
    flash(f'Add-on "{name}" deleted.', 'info')
    return redirect(url_for('admin.addons_index'))


# ==========================================
# ENQUIRIES MANAGEMENT
# ==========================================

@admin_bp.route('/enquiries')
@login_required
def enquiries_list():
    status_filter = request.args.get('status')
    search = request.args.get('q', '').strip()

    query = Enquiry.query
    if status_filter and status_filter in EnquiryStatus.CHOICES:
        query = query.filter_by(status=status_filter)

    if search:
        query = query.filter(
            or_(
                Enquiry.full_name.ilike(f'%{search}%'),
                Enquiry.business_name.ilike(f'%{search}%'),
                Enquiry.reference_code.ilike(f'%{search}%'),
                Enquiry.whatsapp_number.ilike(f'%{search}%')
            )
        )

    enquiries = query.order_by(Enquiry.created_at.desc()).all()
    return render_template(
        'admin/enquiries/index.html',
        enquiries=enquiries,
        current_status=status_filter,
        search=search,
        statuses=EnquiryStatus.CHOICES
    )


@admin_bp.route('/enquiries/<int:enquiry_id>', methods=['GET', 'POST'])
@login_required
def enquiry_detail(enquiry_id):
    enquiry = db.get_or_404(Enquiry, enquiry_id)
    status_form = EnquiryStatusForm()
    status_form.status.choices = [(s, s) for s in EnquiryStatus.CHOICES]
    note_form = EnquiryNoteForm()

    if request.method == 'GET':
        status_form.status.data = enquiry.status

    # Client WhatsApp clean number for one-click chat
    client_whatsapp_clean = clean_phone_number(enquiry.whatsapp_number)

    return render_template(
        'admin/enquiries/detail.html',
        enquiry=enquiry,
        status_form=status_form,
        note_form=note_form,
        client_whatsapp_clean=client_whatsapp_clean,
        statuses=EnquiryStatus.CHOICES
    )


@admin_bp.route('/enquiries/<int:enquiry_id>/update-status', methods=['POST'])
@login_required
def enquiry_update_status(enquiry_id):
    enquiry = db.get_or_404(Enquiry, enquiry_id)
    new_status = request.form.get('status')
    if new_status in EnquiryStatus.CHOICES:
        old_status = enquiry.status
        enquiry.status = new_status
        # Add automated audit note
        note = EnquiryNote(
            enquiry_id=enquiry.id,
            note_text=f"Status changed from '{old_status}' to '{new_status}' by {current_user.username}",
            author_name=current_user.username
        )
        db.session.add(note)
        db.session.commit()
        flash(f'Enquiry status updated to "{new_status}".', 'success')
    return redirect(url_for('admin.enquiry_detail', enquiry_id=enquiry.id))


@admin_bp.route('/enquiries/<int:enquiry_id>/add-note', methods=['POST'])
@login_required
def enquiry_add_note(enquiry_id):
    enquiry = db.get_or_404(Enquiry, enquiry_id)
    note_text = request.form.get('note_text', '').strip()
    if note_text:
        note = EnquiryNote(
            enquiry_id=enquiry.id,
            note_text=note_text,
            author_name=current_user.username
        )
        db.session.add(note)
        db.session.commit()
        flash('Internal note added.', 'success')
    else:
        flash('Note cannot be empty.', 'warning')
    return redirect(url_for('admin.enquiry_detail', enquiry_id=enquiry.id))


# ==========================================
# SITE SETTINGS MANAGEMENT
# ==========================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SiteSettingsForm()
    fields = [
        'brand_name', 'brand_tagline', 'hero_title', 'hero_subtitle',
        'whatsapp_number', 'contact_phone', 'contact_email', 'office_address',
        'currency_symbol', 'instagram_url', 'twitter_url', 'linkedin_url', 'facebook_url'
    ]

    if form.validate_on_submit():
        for field in fields:
            val = getattr(form, field).data
            SiteSetting.set(field, val.strip() if val else "")
        flash('Brand settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))

    elif request.method == 'GET':
        form.brand_name.data = SiteSetting.get('brand_name', 'ShowcaseCraft Studio')
        form.brand_tagline.data = SiteSetting.get('brand_tagline', 'Premium Website Showroom & Client Acquisition Platform')
        form.hero_title.data = SiteSetting.get('hero_title', 'Your Business Deserves More Than Just a Social Media Page.')
        form.hero_subtitle.data = SiteSetting.get('hero_subtitle', 'Professional websites designed to help businesses showcase products, reach customers and grow online.')
        form.whatsapp_number.data = SiteSetting.get('whatsapp_number', '2348000000000')
        form.contact_phone.data = SiteSetting.get('contact_phone', '+234 800 000 0000')
        form.contact_email.data = SiteSetting.get('contact_email', 'hello@showcasecraft.com')
        form.office_address.data = SiteSetting.get('office_address', 'Victoria Island, Lagos, Nigeria')
        form.currency_symbol.data = SiteSetting.get('currency_symbol', '₦')
        form.instagram_url.data = SiteSetting.get('instagram_url', '')
        form.twitter_url.data = SiteSetting.get('twitter_url', '')
        form.linkedin_url.data = SiteSetting.get('linkedin_url', '')
        form.facebook_url.data = SiteSetting.get('facebook_url', '')

    return render_template('admin/settings/index.html', form=form)
