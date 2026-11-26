import hashlib
from datetime import datetime, timedelta, timezone
from flask import request
from sqlalchemy import func
from app.extensions import db
from app.models import WebsiteProject, WebsiteView, Enquiry, WebsiteCategory, EnquiryStatus


def record_project_view(project_id: int):
    """
    Records a page view for a website project.
    Prevents artificial inflation by throttling same IP/User-Agent to 1 view per hour.
    """
    ip = request.remote_addr or 'unknown'
    ua = request.headers.get('User-Agent', '')[:255]
    ip_hash = hashlib.sha256(f"{ip}_{ua}".encode('utf-8')).hexdigest()

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_view = WebsiteView.query.filter(
        WebsiteView.project_id == project_id,
        WebsiteView.ip_hash == ip_hash,
        WebsiteView.created_at >= one_hour_ago
    ).first()

    if not recent_view:
        view = WebsiteView(
            project_id=project_id,
            ip_hash=ip_hash,
            user_agent=ua
        )
        db.session.add(view)
        # Update counter on project
        project = db.session.get(WebsiteProject, project_id)
        if project:
            project.views_count = (project.views_count or 0) + 1
        db.session.commit()


def get_dashboard_metrics():
    """
    Compiles summary analytics for the administrator dashboard.
    """
    total_projects = WebsiteProject.query.count()
    published_projects = WebsiteProject.query.filter_by(is_published=True).count()
    draft_projects = total_projects - published_projects

    total_enquiries = Enquiry.query.count()
    new_enquiries = Enquiry.query.filter_by(status=EnquiryStatus.NEW).count()
    won_enquiries = Enquiry.query.filter_by(status=EnquiryStatus.WON).count()
    
    conversion_rate = (won_enquiries / total_enquiries * 100) if total_enquiries > 0 else 0.0

    # Most viewed showcases
    top_viewed = WebsiteProject.query.filter_by(is_published=True)\
        .order_by(WebsiteProject.views_count.desc())\
        .limit(5).all()

    # Most requested categories based on enquiries
    category_demand = db.session.query(
        WebsiteCategory.name,
        func.count(Enquiry.id).label('enquiry_count')
    ).join(WebsiteProject, WebsiteProject.category_id == WebsiteCategory.id)\
     .join(Enquiry, Enquiry.website_id == WebsiteProject.id)\
     .group_by(WebsiteCategory.name)\
     .order_by(func.count(Enquiry.id).desc())\
     .limit(5).all()

    # Status distribution
    status_counts = db.session.query(
        Enquiry.status,
        func.count(Enquiry.id).label('count')
    ).group_by(Enquiry.status).all()

    status_dict = {status: 0 for status in EnquiryStatus.CHOICES}
    for status, count in status_counts:
        status_dict[status] = count

    return {
        'total_projects': total_projects,
        'published_projects': published_projects,
        'draft_projects': draft_projects,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'won_enquiries': won_enquiries,
        'conversion_rate': round(conversion_rate, 1),
        'top_viewed': top_viewed,
        'category_demand': category_demand,
        'status_counts': status_dict
    }
