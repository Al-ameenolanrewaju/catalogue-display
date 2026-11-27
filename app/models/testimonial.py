from datetime import datetime, timezone
from app.extensions import db


class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_role_company = db.Column(db.String(120), nullable=False)
    avatar_url = db.Column(db.String(300), nullable=True)
    rating = db.Column(db.Integer, default=5, nullable=False)
    content = db.Column(db.Text, nullable=False)
    project_type = db.Column(db.String(80), nullable=True)  # e.g., 'E-Commerce Website', 'Corporate Showroom'
    is_featured = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def stars_range(self):
        return range(max(1, min(5, self.rating or 5)))

    def __repr__(self):
        return f'<Testimonial {self.client_name} ({self.client_role_company})>'
