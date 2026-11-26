from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, make_response
from sqlalchemy import or_
from app.extensions import db
from app.models import (
    WebsiteProject, WebsiteCategory, Package, AddOn,
    Enquiry, EnquiryAddOn, EnquiryStatus, SiteSetting
)
from app.services.analytics_service import record_project_view
from app.services.whatsapp import build_whatsapp_link, generate_whatsapp_message

public_bp = Blueprint('public', __name__)


@public_bp.app_context_processor
def inject_site_settings():
    """Makes configurable branding and settings available to all Jinja templates."""
    return {
        'brand_name': SiteSetting.get('brand_name', 'ApexCraft Studios'),
        'brand_tagline': SiteSetting.get('brand_tagline', 'Turn Browsers Into Buyers With High-Converting Websites'),
        'hero_title': SiteSetting.get('hero_title', 'Your Business Deserves More Than Just a Social Media Page.'),
        'hero_subtitle': SiteSetting.get('hero_subtitle', 'Professional websites designed to help Nigerian and global businesses showcase products, build credibility, and generate paying customers 24/7.'),
        'whatsapp_number': SiteSetting.get('whatsapp_number', '2348000000000'),
        'contact_phone': SiteSetting.get('contact_phone', '+234 800 000 0000'),
        'contact_email': SiteSetting.get('contact_email', 'hello@apexcraft.ng'),
        'office_address': SiteSetting.get('office_address', 'Victoria Island, Lagos, Nigeria'),
        'currency_symbol': SiteSetting.get('currency_symbol', '₦'),
        'instagram_url': SiteSetting.get('instagram_url', '#'),
        'twitter_url': SiteSetting.get('twitter_url', '#'),
        'linkedin_url': SiteSetting.get('linkedin_url', '#'),
        'facebook_url': SiteSetting.get('facebook_url', '#'),
    }


@public_bp.route('/')
def index():
    featured_projects = WebsiteProject.query.filter_by(is_published=True, is_featured=True)\
        .order_by(WebsiteProject.created_at.desc()).limit(6).all()
    
    # If fewer than 4 featured, fill with newest published projects
    if len(featured_projects) < 4:
        featured_ids = [p.id for p in featured_projects]
        fillers = WebsiteProject.query.filter(
            WebsiteProject.is_published == True,
            ~WebsiteProject.id.in_(featured_ids) if featured_ids else True
        ).order_by(WebsiteProject.created_at.desc()).limit(6 - len(featured_projects)).all()
        featured_projects.extend(fillers)

    categories = WebsiteCategory.query.filter_by(is_active=True).order_by(WebsiteCategory.display_order.asc()).all()
    packages = Package.query.filter_by(is_active=True).order_by(Package.display_order.asc()).all()
    addons = AddOn.query.filter_by(is_active=True).order_by(AddOn.display_order.asc()).all()

    return render_template(
        'public/index.html',
        featured_projects=featured_projects,
        categories=categories,
        packages=packages,
        addons=addons
    )


@public_bp.route('/catalogue')
def catalogue():
    search = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'featured')

    query = WebsiteProject.query.filter_by(is_published=True)

    selected_category = None
    if category_slug:
        selected_category = WebsiteCategory.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    if search:
        query = query.filter(
            or_(
                WebsiteProject.title.ilike(f'%{search}%'),
                WebsiteProject.intended_business_type.ilike(f'%{search}%'),
                WebsiteProject.short_description.ilike(f'%{search}%'),
                WebsiteProject.full_description.ilike(f'%{search}%')
            )
        )

    if sort_by == 'newest':
        query = query.order_by(WebsiteProject.created_at.desc())
    elif sort_by == 'views':
        query = query.order_by(WebsiteProject.views_count.desc())
    elif sort_by == 'title':
        query = query.order_by(WebsiteProject.title.asc())
    else:  # featured first
        query = query.order_by(WebsiteProject.is_featured.desc(), WebsiteProject.created_at.desc())

    projects = query.all()
    categories = WebsiteCategory.query.filter_by(is_active=True).order_by(WebsiteCategory.display_order.asc()).all()

    return render_template(
        'public/catalogue.html',
        projects=projects,
        categories=categories,
        selected_category=selected_category,
        search=search,
        sort_by=sort_by
    )


@public_bp.route('/showcase/<slug>')
def showcase_detail(slug):
    project = WebsiteProject.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Record anonymized page view
    try:
        record_project_view(project.id)
    except Exception:
        pass

    # Related designs from same category
    related_projects = WebsiteProject.query.filter(
        WebsiteProject.is_published == True,
        WebsiteProject.category_id == project.category_id,
        WebsiteProject.id != project.id
    ).limit(3).all()

    packages = Package.query.filter_by(is_active=True).order_by(Package.display_order.asc()).all()
    addons = AddOn.query.filter_by(is_active=True).order_by(AddOn.display_order.asc()).all()

    return render_template(
        'public/showcase_detail.html',
        project=project,
        related_projects=related_projects,
        packages=packages,
        addons=addons
    )


@public_bp.route('/preview/<slug>')
def live_preview(slug):
    project = WebsiteProject.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('public/live_preview.html', project=project)


@public_bp.route('/packages')
def packages():
    packages_list = Package.query.filter_by(is_active=True).order_by(Package.display_order.asc()).all()
    addons = AddOn.query.filter_by(is_active=True).order_by(AddOn.display_order.asc()).all()
    return render_template('public/packages.html', packages=packages_list, addons=addons)


@public_bp.route('/enquire', methods=['GET', 'POST'])
@public_bp.route('/contact', methods=['GET', 'POST'])
def enquire():
    # Pre-selections from query params
    preselected_website_slug = request.args.get('website', '').strip()
    preselected_package_slug = request.args.get('package', '').strip()

    preselected_website = None
    if preselected_website_slug:
        preselected_website = WebsiteProject.query.filter_by(slug=preselected_website_slug, is_published=True).first()

    preselected_package = None
    if preselected_package_slug:
        preselected_package = Package.query.filter_by(slug=preselected_package_slug, is_active=True).first()

    all_websites = WebsiteProject.query.filter_by(is_published=True).order_by(WebsiteProject.title.asc()).all()
    all_packages = Package.query.filter_by(is_active=True).order_by(Package.display_order.asc()).all()
    all_addons = AddOn.query.filter_by(is_active=True).order_by(AddOn.display_order.asc()).all()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        business_name = request.form.get('business_name', '').strip()
        whatsapp_number = request.form.get('whatsapp_number', '').strip()
        email = request.form.get('email', '').strip() or None
        
        website_id_val = request.form.get('website_id', '').strip()
        website_id = int(website_id_val) if website_id_val and website_id_val.isdigit() else None
        
        package_id_val = request.form.get('package_id', '').strip()
        package_id = int(package_id_val) if package_id_val and package_id_val.isdigit() else None

        additional_requirements = request.form.get('additional_requirements', '').strip()
        estimated_budget = request.form.get('estimated_budget', '').strip() or None

        # Validation
        if not full_name or not business_name or not whatsapp_number:
            flash('Please complete your Name, Business Name, and WhatsApp number.', 'danger')
            return redirect(request.url)

        # Selected add-ons
        selected_addon_ids = request.form.getlist('addon_ids')

        # Calculate estimated total
        calculated_estimate = 0.0
        has_estimate = False

        if package_id:
            pkg = db.session.get(Package, package_id)
            if pkg and pkg.price:
                calculated_estimate += float(pkg.price)
                has_estimate = True

        enquiry = Enquiry(
            reference_code=Enquiry.generate_reference(),
            full_name=full_name,
            business_name=business_name,
            whatsapp_number=whatsapp_number,
            email=email,
            website_id=website_id,
            package_id=package_id,
            additional_requirements=additional_requirements,
            estimated_budget=estimated_budget,
            status=EnquiryStatus.NEW
        )
        db.session.add(enquiry)
        db.session.flush()

        for addon_id_str in selected_addon_ids:
            try:
                aid = int(addon_id_str)
                addon_obj = db.session.get(AddOn, aid)
                if addon_obj:
                    price_val = float(addon_obj.price) if addon_obj.price is not None else None
                    if price_val:
                        calculated_estimate += price_val
                        has_estimate = True
                    ea = EnquiryAddOn(
                        enquiry_id=enquiry.id,
                        add_on_id=aid,
                        price_at_enquiry=price_val
                    )
                    db.session.add(ea)
            except (ValueError, TypeError):
                continue

        enquiry.calculated_estimate = calculated_estimate if has_estimate else None
        db.session.commit()

        return redirect(url_for('public.enquiry_confirmation', reference_code=enquiry.reference_code))

    return render_template(
        'public/contact.html',
        all_websites=all_websites,
        all_packages=all_packages,
        all_addons=all_addons,
        preselected_website=preselected_website,
        preselected_package=preselected_package
    )


@public_bp.route('/enquiry/confirmation/<reference_code>')
def enquiry_confirmation(reference_code):
    enquiry = Enquiry.query.filter_by(reference_code=reference_code).first_or_404()
    brand_phone = SiteSetting.get('whatsapp_number', '2348000000000')
    brand_name = SiteSetting.get('brand_name', 'ApexCraft Studios')
    whatsapp_url = build_whatsapp_link(brand_phone, enquiry, brand_name)

    return render_template(
        'public/enquiry_confirmation.html',
        enquiry=enquiry,
        whatsapp_url=whatsapp_url
    )


@public_bp.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: " + request.url_root.rstrip('/') + "/sitemap.xml\n"
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain"
    return response


@public_bp.route('/sitemap.xml')
def sitemap():
    projects = WebsiteProject.query.filter_by(is_published=True).all()
    categories = WebsiteCategory.query.filter_by(is_active=True).all()
    
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    base = request.url_root.rstrip('/')
    
    # Core pages
    core_routes = ['public.index', 'public.catalogue', 'public.packages', 'public.enquire']
    for r in core_routes:
        xml_parts.append(f'<url><loc>{base}{url_for(r)}</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>')
        
    for p in projects:
        xml_parts.append(f'<url><loc>{base}{url_for("public.showcase_detail", slug=p.slug)}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')

    xml_parts.append('</urlset>')
    
    response = make_response("".join(xml_parts))
    response.headers["Content-Type"] = "application/xml"
    return response
