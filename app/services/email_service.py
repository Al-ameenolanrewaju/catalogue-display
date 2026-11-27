import os
import logging
from app.models import SiteSetting
import resend

logger = logging.getLogger(__name__)


def get_resend_client():
    """Initializes and returns the resend module if a valid API key is present."""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not api_key or api_key == 're_your_api_key_here' or not api_key.startswith('re_'):
        return None
    resend.api_key = api_key
    return resend


def send_admin_enquiry_alert(enquiry, brand_name=None):
    """Sends a rich HTML email alert to the admin when a new inquiry is submitted."""
    client = get_resend_client()
    if not client:
        logger.info("Resend API key not configured. Skipping email dispatch.")
        return False

    if not brand_name:
        brand_name = SiteSetting.get('brand_name', 'ApexCraft Studios')

    from_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev').strip()
    admin_email = os.environ.get(
        'ADMIN_NOTIFICATION_EMAIL',
        os.environ.get('ADMIN_EMAIL', SiteSetting.get('contact_email', 'admin@apexcraft.ng'))
    ).strip()

    subject = f"🔥 New Website Lead: {enquiry.business_name} ({enquiry.full_name})"

    # Format addons
    addons_list = [ea.add_on.name for ea in enquiry.addons if ea.add_on] if hasattr(enquiry, 'addons') and enquiry.addons else []
    addons_str = ", ".join(addons_list) if addons_list else "None selected"

    website_title = enquiry.website.title if enquiry.website else "General / Custom Project"
    package_name = enquiry.package.name if enquiry.package else "Custom Quotation"
    estimate_str = f"₦{enquiry.calculated_estimate:,.0f}" if enquiry.calculated_estimate else "Quote Upon Review"
    clean_phone = enquiry.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #FAF8F5; margin: 0; padding: 24px; color: #1C1917; }}
        .card {{ background: #FFFFFF; max-width: 600px; margin: 0 auto; border-radius: 12px; border: 1px solid #E2DDD5; padding: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
        .header {{ border-bottom: 2px solid #B8860B; padding-bottom: 16px; margin-bottom: 24px; }}
        .title {{ color: #1C1917; font-size: 20px; font-weight: 700; margin: 0; }}
        .badge {{ background-color: #FDF9F0; color: #B8860B; border: 1px solid #C59B27; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
        .item {{ margin-bottom: 16px; }}
        .label {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: #78716C; margin-bottom: 4px; }}
        .value {{ font-size: 15px; color: #1C1917; font-weight: 500; }}
        .highlight {{ color: #B8860B; font-weight: 700; font-size: 18px; }}
        .btn {{ display: inline-block; background-color: #25D366; color: #FFFFFF !important; font-weight: 600; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 16px; }}
        .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #E2DDD5; font-size: 12px; color: #A8A29E; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <span class="badge">New Client Lead</span>
          <h2 class="title" style="margin-top: 8px;">Website Inquiry for {enquiry.business_name}</h2>
        </div>

        <div class="item">
          <div class="label">Client Contact</div>
          <div class="value"><strong>{enquiry.full_name}</strong></div>
          <div class="value">WhatsApp: <strong>{enquiry.whatsapp_number}</strong></div>
          {f'<div class="value">Email: {enquiry.email}</div>' if enquiry.email else ''}
        </div>

        <div class="item">
          <div class="label">Showcase Concept</div>
          <div class="value">{website_title}</div>
        </div>

        <div class="item">
          <div class="label">Package & Estimate</div>
          <div class="value">{package_name} &bull; <span class="highlight">{estimate_str}</span></div>
        </div>

        <div class="item">
          <div class="label">Selected Add-ons</div>
          <div class="value">{addons_str}</div>
        </div>

        {f'''
        <div class="item">
          <div class="label">Client Project Brief</div>
          <div class="value" style="background: #F4EFE6; padding: 12px; border-radius: 6px; font-size: 14px; white-space: pre-wrap;">{enquiry.additional_requirements}</div>
        </div>
        ''' if enquiry.additional_requirements else ''}

        <div style="text-align: center; margin-top: 24px;">
          <a href="https://wa.me/{clean_phone}" class="btn">
            Chat with {enquiry.full_name} on WhatsApp
          </a>
        </div>

        <div class="footer">
          Received via {brand_name} Showroom Platform &bull; Ref: {enquiry.reference_code}
        </div>
      </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": from_email,
            "to": [admin_email],
            "subject": subject,
            "html": html_content,
        }
        res = client.Emails.send(params)
        logger.info(f"Resend admin notification sent successfully: {res}")
        return True
    except Exception as e:
        logger.error(f"Failed to send admin notification via Resend: {e}")
        return False


def send_client_confirmation_email(enquiry, brand_name=None):
    """Sends a professional confirmation email to prospective client if an email was provided."""
    if not enquiry.email:
        return False

    client = get_resend_client()
    if not client:
        return False

    if not brand_name:
        brand_name = SiteSetting.get('brand_name', 'ApexCraft Studios')

    from_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev').strip()
    subject = f"We Received Your Website Inquiry — {brand_name}"

    package_name = enquiry.package.name if enquiry.package else "Custom Website Project"
    estimate_str = f"₦{enquiry.calculated_estimate:,.0f}" if enquiry.calculated_estimate else "Quote Upon Review"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #FAF8F5; margin: 0; padding: 24px; color: #1C1917; }}
        .card {{ background: #FFFFFF; max-width: 600px; margin: 0 auto; border-radius: 12px; border: 1px solid #E2DDD5; padding: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
        .header {{ border-bottom: 2px solid #B8860B; padding-bottom: 16px; margin-bottom: 24px; text-align: center; }}
        .title {{ color: #1C1917; font-size: 22px; font-weight: 700; margin: 0; }}
        .lead {{ font-size: 15px; line-height: 1.6; color: #44403C; }}
        .summary-box {{ background-color: #FAF8F2; border: 1px solid #E2DDD5; border-radius: 8px; padding: 16px; margin: 20px 0; }}
        .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #E2DDD5; font-size: 12px; color: #78716C; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h2 class="title">{brand_name}</h2>
          <div style="color: #B8860B; font-weight: 600; font-size: 14px; margin-top: 4px;">Website Showroom & Client Acquisition</div>
        </div>

        <p class="lead">Hello <strong>{enquiry.full_name}</strong>,</p>
        <p class="lead">Thank you for submitting your project brief for <strong>{enquiry.business_name}</strong>. We have received your inquiry and our team is already reviewing your requirements.</p>

        <div class="summary-box">
          <div style="font-weight: 700; margin-bottom: 8px; color: #1C1917;">Your Project Intake Summary:</div>
          <div>&bull; <strong>Package:</strong> {package_name}</div>
          <div>&bull; <strong>Estimated Investment:</strong> {estimate_str}</div>
          <div>&bull; <strong>Reference Code:</strong> {enquiry.reference_code}</div>
        </div>

        <p class="lead"><strong>What happens next?</strong><br>
        We will reach out to you via WhatsApp at <strong>{enquiry.whatsapp_number}</strong> within business hours with a clear milestone breakdown, timeline, and exact proposal.</p>

        <p class="lead">Best regards,<br><strong>The {brand_name} Team</strong></p>

        <div class="footer">
          &copy; {brand_name}. All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": from_email,
            "to": [enquiry.email],
            "subject": subject,
            "html": html_content,
        }
        res = client.Emails.send(params)
        logger.info(f"Resend client confirmation sent successfully to {enquiry.email}: {res}")
        return True
    except Exception as e:
        logger.error(f"Failed to send client confirmation via Resend: {e}")
        return False
