from datetime import datetime, timezone
from app.extensions import db


class AddOn(db.Model):
    __tablename__ = 'add_ons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)  # In NGN, can be None for custom/varies
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    enquiry_addons = db.relationship('EnquiryAddOn', back_populates='add_on', cascade='all, delete-orphan')

    @property
    def formatted_price(self) -> str:
        if self.price is None or self.price == 0:
            return "Quotation on Request"
        return f"₦{self.price:,.0f}"

    def __repr__(self):
        return f'<AddOn {self.name}>'
