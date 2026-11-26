from datetime import datetime, timezone
import re
from app.extensions import db


class WebsiteCategory(db.Model):
    __tablename__ = 'website_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    projects = db.relationship('WebsiteProject', back_populates='category', cascade='all, delete-orphan', lazy='dynamic')

    @staticmethod
    def generate_slug(name: str) -> str:
        s = re.sub(r'[^\w\s-]', '', name).strip().lower()
        return re.sub(r'[-\s]+', '-', s)

    @property
    def published_projects_count(self) -> int:
        return self.projects.filter_by(is_published=True).count()

    def __repr__(self):
        return f'<WebsiteCategory {self.name}>'
