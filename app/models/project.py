from datetime import datetime, timezone
import re
from app.extensions import db


class WebsiteProject(db.Model):
    __tablename__ = 'website_projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(255), nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('website_categories.id', ondelete='SET NULL'), nullable=True)
    live_demo_url = db.Column(db.String(500), nullable=True)
    intended_business_type = db.Column(db.String(150), nullable=False)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    is_published = db.Column(db.Boolean, default=True, index=True)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = db.relationship('WebsiteCategory', back_populates='projects')
    images = db.relationship('WebsiteImage', back_populates='project', cascade='all, delete-orphan', order_by='WebsiteImage.display_order')
    features = db.relationship('ProjectFeature', back_populates='project', cascade='all, delete-orphan', order_by='ProjectFeature.display_order')
    enquiries = db.relationship('Enquiry', back_populates='website', lazy='dynamic')
    views = db.relationship('WebsiteView', back_populates='project', cascade='all, delete-orphan', lazy='dynamic')

    @staticmethod
    def generate_slug(title: str) -> str:
        s = re.sub(r'[^\w\s-]', '', title).strip().lower()
        return re.sub(r'[-\s]+', '-', s)

    @property
    def primary_image(self):
        for img in self.images:
            if img.is_primary:
                return img
        return self.images[0] if self.images else None

    @property
    def primary_image_url(self):
        primary = self.primary_image
        if primary:
            return primary.image_url
        return 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80'

    def __repr__(self):
        return f'<WebsiteProject {self.title}>'


class WebsiteImage(db.Model):
    __tablename__ = 'website_images'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('website_projects.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    project = db.relationship('WebsiteProject', back_populates='images')

    def __repr__(self):
        return f'<WebsiteImage {self.id} for Project {self.project_id}>'


class ProjectFeature(db.Model):
    __tablename__ = 'project_features'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('website_projects.id', ondelete='CASCADE'), nullable=False)
    feature_text = db.Column(db.String(255), nullable=False)
    display_order = db.Column(db.Integer, default=0)

    project = db.relationship('WebsiteProject', back_populates='features')

    def __repr__(self):
        return f'<ProjectFeature {self.feature_text}>'
