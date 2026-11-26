from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app.extensions import db
from app.models import WebsiteProject, WebsiteCategory, Package, AddOn

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/websites')
def api_websites():
    query_str = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()

    query = WebsiteProject.query.filter_by(is_published=True)

    if category_slug:
        cat = WebsiteCategory.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    if query_str:
        query = query.filter(
            or_(
                WebsiteProject.title.ilike(f'%{query_str}%'),
                WebsiteProject.intended_business_type.ilike(f'%{query_str}%'),
                WebsiteProject.short_description.ilike(f'%{query_str}%')
            )
        )

    projects = query.order_by(WebsiteProject.is_featured.desc(), WebsiteProject.created_at.desc()).all()

    data = []
    for p in projects:
        data.append({
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'intended_business_type': p.intended_business_type,
            'short_description': p.short_description,
            'category_name': p.category.name if p.category else 'General',
            'category_slug': p.category.slug if p.category else '',
            'primary_image_url': p.primary_image_url,
            'live_demo_url': p.live_demo_url,
            'is_featured': p.is_featured,
            'features': [f.feature_text for f in p.features[:3]]
        })

    return jsonify({'count': len(data), 'websites': data})


@api_bp.route('/calculate-estimate', methods=['POST'])
def calculate_estimate():
    data = request.get_json() or {}
    package_id = data.get('package_id')
    addon_ids = data.get('addon_ids', [])

    total = 0.0
    package_price = None

    if package_id:
        pkg = db.session.get(Package, package_id)
        if pkg and pkg.price:
            package_price = float(pkg.price)
            total += package_price

    addon_items = []
    for aid in addon_ids:
        add = db.session.get(AddOn, aid)
        if add:
            p = float(add.price) if add.price is not None else 0.0
            total += p
            addon_items.append({'id': add.id, 'name': add.name, 'price': p})

    return jsonify({
        'package_price': package_price,
        'addons': addon_items,
        'estimated_total': total,
        'formatted_total': f"₦{total:,.0f}" if total > 0 else "Quotation on Request"
    })
