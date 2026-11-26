from datetime import datetime, timezone
from app.extensions import db


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)  # In NGN, None for custom quote
    is_recommended = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    features = db.relationship('PackageFeature', back_populates='package', cascade='all, delete-orphan', order_by='PackageFeature.display_order')
    enquiries = db.relationship('Enquiry', back_populates='package', lazy='dynamic')

    @property
    def formatted_price(self) -> str:
        if self.price is None or self.price == 0:
            return "Custom Quote"
        return f"₦{self.price:,.0f}"

    def __repr__(self):
        return f'<Package {self.name}>'


class PackageFeature(db.Model):
    __tablename__ = 'package_features'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id', ondelete='CASCADE'), nullable=False)
    feature_text = db.Column(db.String(255), nullable=False)
    is_included = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)

    package = db.relationship('Package', back_populates='features')

    def __repr__(self):
        return f'<PackageFeature {self.feature_text}>'
