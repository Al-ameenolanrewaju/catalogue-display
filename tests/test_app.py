import pytest
from app import create_app
from app.config import Config
from app.extensions import db
from app.models import (
    AdminUser, WebsiteCategory, WebsiteProject, Package, 
    AddOn, Enquiry, EnquiryStatus, SiteSetting
)
from seeds.seed_data import seed_database
from app.services.whatsapp import clean_phone_number, generate_whatsapp_message, build_whatsapp_link


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_public_routes(client):
    """Verifies that all public pages render successfully."""
    # 1. Homepage
    res = client.get('/')
    assert res.status_code == 200
    assert b"Your Business Deserves More Than Just a Social Media Page" in res.data
    assert b"Featured Website Showcases" in res.data
    assert b"Frequently Asked Questions" in res.data

    # 2. Catalogue
    res = client.get('/catalogue')
    assert res.status_code == 200
    assert b"Explore Website Designs" in res.data
    assert b"Aura Atelier Luxury Fashion" in res.data

    # 3. Packages page
    res = client.get('/packages')
    assert res.status_code == 200
    assert b"Website Packages & Transparent Pricing" in res.data
    assert b"Basic Website" in res.data
    assert b"Standard E-commerce" in res.data

    # 4. Contact / Enquiry page
    res = client.get('/contact')
    assert res.status_code == 200
    assert b"Request Your Website Quotation" in res.data

    # 5. Robots & Sitemap
    assert client.get('/robots.txt').status_code == 200
    assert client.get('/sitemap.xml').status_code == 200


def test_catalogue_search_and_filter(client):
    """Verifies searching and category filtering in the catalogue."""
    # Search by keyword
    res = client.get('/catalogue?q=Fashion')
    assert res.status_code == 200
    assert b"Aura Atelier" in res.data

    # Filter by category
    res = client.get('/catalogue?category=automotive')
    assert res.status_code == 200
    assert b"Velocity Apex Motors" in res.data

    # Sort
    res = client.get('/catalogue?sort=newest')
    assert res.status_code == 200


def test_showcase_detail_and_live_preview(client):
    """Verifies showcase detail view and live demo iframe frame."""
    project = WebsiteProject.query.filter_by(slug='aura-atelier-luxury-fashion').first()
    assert project is not None

    res = client.get(f'/showcase/{project.slug}')
    assert res.status_code == 200
    assert project.title.encode('utf-8') in res.data
    assert b"Get a Website Like This" in res.data
    assert b"Desktop" in res.data
    assert b"Mobile" in res.data

    # Live demo frame
    preview_res = client.get(f'/preview/{project.slug}')
    assert preview_res.status_code == 200
    assert b"Live Interactive Demo" in preview_res.data


def test_enquiry_submission_and_whatsapp(client):
    """Tests client enquiry submission, calculations, and WhatsApp link generation."""
    project = WebsiteProject.query.first()
    package = Package.query.filter_by(slug='standard').first()
    addon = AddOn.query.first()

    post_data = {
        'full_name': 'Adebayo Johnson',
        'business_name': 'Adebayo Global Ltd',
        'whatsapp_number': '08023456789',
        'email': 'adebayo@gmail.com',
        'website_id': str(project.id),
        'package_id': str(package.id),
        'addon_ids': [str(addon.id)],
        'additional_requirements': 'Need payment integration with Paystack.',
        'estimated_budget': '₦200,000 - ₦400,000'
    }

    res = client.post('/enquire', data=post_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Enquiry Received" in res.data
    assert b"Continue to WhatsApp with Enquiry Details" in res.data

    # Check database record
    enquiry = Enquiry.query.filter_by(whatsapp_number='08023456789').first()
    assert enquiry is not None
    assert enquiry.business_name == 'Adebayo Global Ltd'
    assert enquiry.package_id == package.id
    assert enquiry.website_id == project.id
    assert enquiry.status == EnquiryStatus.NEW
    assert len(enquiry.addons) == 1

    # Verify calculated estimate
    expected_total = float(package.price) + float(addon.price)
    assert enquiry.calculated_estimate == expected_total

    # Verify WhatsApp message generator
    wa_msg = generate_whatsapp_message(enquiry, brand_name='ApexCraft')
    assert "Adebayo Global Ltd" in wa_msg
    assert enquiry.reference_code in wa_msg
    assert package.name in wa_msg


def test_admin_authentication_and_dashboard(client):
    """Tests admin authentication, session guarding, and dashboard metrics."""
    # Attempt unauthorized access
    unauth_res = client.get('/admin/', follow_redirects=True)
    assert b"Please log in to access the administration dashboard" in unauth_res.data

    # Login with wrong credentials
    bad_login = client.post('/admin/login', data={'identity': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
    assert b"Invalid username/email or password" in bad_login.data

    # Login with correct credentials
    good_login = client.post('/admin/login', data={'identity': 'admin', 'password': 'AdminSecure2026!'}, follow_redirects=True)
    assert good_login.status_code == 200
    assert b"Dashboard Overview" in good_login.data
    assert b"Published Showcases" in good_login.data


def test_admin_crud_operations(client):
    """Tests administrative CRUD: websites, categories, packages, add-ons, enquiry updates, and settings."""
    # Login first
    client.post('/admin/login', data={'identity': 'admin', 'password': 'AdminSecure2026!'}, follow_redirects=True)

    # 1. Create a new website showcase
    new_website_data = {
        'title': 'Solaris Green Energy Portal',
        'category_id': '1',
        'intended_business_type': 'Solar Inverter Retailers & Installers',
        'short_description': 'Clean solar product catalogue with power capacity estimator.',
        'full_description': 'A tailored showroom for solar companies to calculate load requirements.',
        'live_demo_url': 'https://example.com/demo',
        'features': 'Load Calculator\nBattery Spec Sheet\nWhatsApp Consultation',
        'primary_image_url': 'https://images.unsplash.com/photo-1509391365360-2e959784a276',
        'is_featured': True,
        'is_published': True
    }
    create_res = client.post('/admin/websites/new', data=new_website_data, follow_redirects=True)
    assert create_res.status_code == 200
    created_proj = WebsiteProject.query.filter_by(title='Solaris Green Energy Portal').first()
    assert created_proj is not None
    assert len(created_proj.features) == 3

    # Toggle publish status
    toggle_res = client.post(f'/admin/websites/{created_proj.id}/toggle-status', follow_redirects=True)
    assert toggle_res.status_code == 200
    db.session.refresh(created_proj)
    assert created_proj.is_published is False

    # 2. Add Category
    cat_res = client.post('/admin/categories', data={
        'name': 'Healthcare & Pharmacy',
        'description': 'Hospitals, medical clinics, and pharmacy stores.',
        'display_order': 10,
        'is_active': True
    }, follow_redirects=True)
    assert cat_res.status_code == 200
    assert WebsiteCategory.query.filter_by(name='Healthcare & Pharmacy').first() is not None

    # 3. Create Package
    pkg_res = client.post('/admin/packages/new', data={
        'name': 'Ultimate Enterprise Portal',
        'slug': 'ultimate-enterprise',
        'description': 'Full stack bespoke platform.',
        'price': '850000',
        'is_recommended': True,
        'display_order': 5,
        'is_active': True,
        'features': 'Full Stack Portal\nCustom API\n- Excluded Item'
    }, follow_redirects=True)
    assert pkg_res.status_code == 200
    new_pkg = Package.query.filter_by(slug='ultimate-enterprise').first()
    assert new_pkg is not None
    assert new_pkg.price == 850000.0

    # 4. Update Enquiry Status & Add Internal Note
    enquiry = Enquiry(
        reference_code='ENQ-TEST-001',
        full_name='Test Client',
        business_name='Test Business',
        whatsapp_number='08011112222',
        status=EnquiryStatus.NEW
    )
    db.session.add(enquiry)
    db.session.commit()

    # Update status to Quotation Sent
    status_res = client.post(f'/admin/enquiries/{enquiry.id}/update-status', data={'status': EnquiryStatus.QUOTATION_SENT}, follow_redirects=True)
    assert status_res.status_code == 200
    db.session.refresh(enquiry)
    assert enquiry.status == EnquiryStatus.QUOTATION_SENT

    # Add note
    note_res = client.post(f'/admin/enquiries/{enquiry.id}/add-note', data={'note_text': 'Followed up on WhatsApp.'}, follow_redirects=True)
    assert note_res.status_code == 200
    db.session.refresh(enquiry)
    assert len(enquiry.notes) >= 2  # status audit note + custom note

    # 5. Site Settings (Configurable brand identity without code changes)
    settings_res = client.post('/admin/settings', data={
        'brand_name': 'ElevateCraft Digital Showroom',
        'brand_tagline': 'Nigeria No. 1 Client Acquisition Platform',
        'hero_title': 'Transform Your Business With a Standalone Website Showroom',
        'hero_subtitle': 'Showcase real products and close clients online.',
        'whatsapp_number': '2348099998888',
        'contact_phone': '+234 809 999 8888',
        'contact_email': 'contact@elevatecraft.ng',
        'office_address': 'Ikeja GRA, Lagos, Nigeria',
        'currency_symbol': '₦',
        'instagram_url': 'https://instagram.com/elevatecraft',
        'twitter_url': '',
        'linkedin_url': '',
        'facebook_url': ''
    }, follow_redirects=True)
    assert settings_res.status_code == 200
    assert SiteSetting.get('brand_name') == 'ElevateCraft Digital Showroom'
    assert SiteSetting.get('whatsapp_number') == '2348099998888'

    # Check updated brand appears on public page without code edit!
    home_res = client.get('/')
    assert b"ElevateCraft Digital Showroom" in home_res.data


def test_resend_email_service(app, monkeypatch):
    """Verifies that Resend email dispatch functions handle configuration states and formatting gracefully."""
    from app.services.email_service import send_admin_enquiry_alert, send_client_confirmation_email
    import resend

    with app.app_context():
        enquiry = Enquiry(
            full_name="Emeka Adeleke",
            business_name="Adeleke Fashion",
            whatsapp_number="08012345678",
            email="emeka@example.com",
            additional_requirements="Need Paystack and WhatsApp checkout.",
            reference_code="ENQ-TEST-1234"
        )
        db.session.add(enquiry)
        db.session.commit()

        # 1. Without API key configured -> returns False safely, does not crash
        monkeypatch.delenv('RESEND_API_KEY', raising=False)
        assert send_admin_enquiry_alert(enquiry) is False
        assert send_client_confirmation_email(enquiry) is False

        # 2. Mock Resend send with active key
        monkeypatch.setenv('RESEND_API_KEY', 're_test_mock_key_12345')
        monkeypatch.setenv('ADMIN_NOTIFICATION_EMAIL', 'staff@test.com')

        sent_calls = []

        def mock_send(params):
            sent_calls.append(params)
            return {"id": "msg_mock_123"}

        monkeypatch.setattr(resend.Emails, 'send', mock_send)

        # Test admin alert
        assert send_admin_enquiry_alert(enquiry, brand_name="ApexCraft Studios") is True
        assert len(sent_calls) == 1
        assert "New Website Lead" in sent_calls[0]["subject"]
        assert sent_calls[0]["to"] == ["staff@test.com"]
        assert enquiry.full_name in sent_calls[0]["html"]

        # Test client confirmation
        assert send_client_confirmation_email(enquiry, brand_name="ApexCraft Studios") is True
        assert len(sent_calls) == 2
        assert "We Received Your Website Inquiry" in sent_calls[1]["subject"]
        assert sent_calls[1]["to"] == [enquiry.email]
