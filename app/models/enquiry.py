from datetime import datetime, timezone
import random
import string
from app.extensions import db


class EnquiryStatus:
    NEW = 'New'
    CONTACTED = 'Contacted'
    QUOTATION_SENT = 'Quotation Sent'
    NEGOTIATING = 'Negotiating'
    WON = 'Won'
    LOST = 'Lost'

    CHOICES = [NEW, CONTACTED, QUOTATION_SENT, NEGOTIATING, WON, LOST]


class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    whatsapp_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    website_id = db.Column(db.Integer, db.ForeignKey('website_projects.id', ondelete='SET NULL'), nullable=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id', ondelete='SET NULL'), nullable=True)
    
    additional_requirements = db.Column(db.Text, nullable=True)
    estimated_budget = db.Column(db.String(100), nullable=True)
    calculated_estimate = db.Column(db.Float, nullable=True)
    
    status = db.Column(db.String(50), default=EnquiryStatus.NEW, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    website = db.relationship('WebsiteProject', back_populates='enquiries')
    package = db.relationship('Package', back_populates='enquiries')
    addons = db.relationship('EnquiryAddOn', back_populates='enquiry', cascade='all, delete-orphan')
    notes = db.relationship('EnquiryNote', back_populates='enquiry', cascade='all, delete-orphan', order_by='EnquiryNote.created_at.desc()')

    @staticmethod
    def generate_reference() -> str:
        chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ENQ-{datetime.now().year}-{chars}"

    @property
    def status_badge_class(self) -> str:
        mapping = {
            EnquiryStatus.NEW: 'bg-primary text-white',
            EnquiryStatus.CONTACTED: 'bg-info text-dark',
            EnquiryStatus.QUOTATION_SENT: 'bg-warning text-dark',
            EnquiryStatus.NEGOTIATING: 'bg-secondary text-white',
            EnquiryStatus.WON: 'bg-success text-white',
            EnquiryStatus.LOST: 'bg-danger text-white'
        }
        return mapping.get(self.status, 'bg-light text-dark')

    def __repr__(self):
        return f'<Enquiry {self.reference_code} - {self.business_name}>'


class EnquiryAddOn(db.Model):
    __tablename__ = 'enquiry_addons'

    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey('enquiries.id', ondelete='CASCADE'), nullable=False)
    add_on_id = db.Column(db.Integer, db.ForeignKey('add_ons.id', ondelete='CASCADE'), nullable=False)
    price_at_enquiry = db.Column(db.Float, nullable=True)

    enquiry = db.relationship('Enquiry', back_populates='addons')
    add_on = db.relationship('AddOn', back_populates='enquiry_addons')

    def __repr__(self):
        return f'<EnquiryAddOn enq={self.enquiry_id} addon={self.add_on_id}>'


class EnquiryNote(db.Model):
    __tablename__ = 'enquiry_notes'

    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey('enquiries.id', ondelete='CASCADE'), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(100), default='Administrator')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    enquiry = db.relationship('Enquiry', back_populates='notes')

    def __repr__(self):
        return f'<EnquiryNote {self.id} for Enquiry {self.enquiry_id}>'
