from datetime import datetime, timezone
from app.extensions import db


class WebsiteView(db.Model):
    __tablename__ = 'website_views'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('website_projects.id', ondelete='CASCADE'), nullable=False, index=True)
    ip_hash = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    project = db.relationship('WebsiteProject', back_populates='views')

    def __repr__(self):
        return f'<WebsiteView project={self.project_id} at {self.created_at}>'
