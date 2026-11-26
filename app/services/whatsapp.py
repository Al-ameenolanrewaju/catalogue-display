import urllib.parse
import re


def clean_phone_number(phone: str, default_country_code: str = "234") -> str:
    """
    Cleans and normalizes phone numbers, specifically handling Nigerian prefixes.
    e.g. '08012345678' -> '2348012345678'
    '+234 801 234 5678' -> '2348012345678'
    """
    if not phone:
        return ""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('0') and len(digits) == 11:
        digits = default_country_code + digits[1:]
    elif digits.startswith(default_country_code):
        pass
    elif not digits.startswith(default_country_code) and len(digits) == 10:
        digits = default_country_code + digits
    return digits


def generate_whatsapp_message(enquiry, brand_name: str = "ApexCraft") -> str:
    """
    Builds a professional, clean WhatsApp message for the enquiry.
    """
    lines = [
        f"👋 *New Website Enquiry - {brand_name}*",
        f"📋 *Reference:* #{enquiry.reference_code}",
        f"━━━━━━━━━━━━━━━━━━",
        f"👤 *Client Name:* {enquiry.full_name}",
        f"🏢 *Business:* {enquiry.business_name}",
        f"📞 *WhatsApp:* {enquiry.whatsapp_number}",
    ]

    if enquiry.email:
        lines.append(f"✉️ *Email:* {enquiry.email}")

    if enquiry.website:
        lines.append(f"🌐 *Interested Design:* {enquiry.website.title} ({enquiry.website.category.name if enquiry.website.category else 'General'})")
    else:
        lines.append("🌐 *Interested Design:* Custom / General Consultation")

    if enquiry.package:
        price_str = enquiry.package.formatted_price
        lines.append(f"📦 *Selected Package:* {enquiry.package.name} ({price_str})")
    else:
        lines.append("📦 *Selected Package:* Not specified / Custom quotation")

    if enquiry.addons:
        addon_names = [f"• {ea.add_on.name}" for ea in enquiry.addons if ea.add_on]
        lines.append(f"⚡ *Selected Add-Ons:*\n" + "\n".join(addon_names))

    if enquiry.calculated_estimate:
        lines.append(f"💰 *Estimated Total:* ₦{enquiry.calculated_estimate:,.0f} (Subject to confirmation)")

    if enquiry.estimated_budget:
        lines.append(f"🎯 *Client Budget Range:* {enquiry.estimated_budget}")

    if enquiry.additional_requirements:
        lines.append(f"📝 *Requirements & Notes:*\n{enquiry.additional_requirements.strip()}")

    lines.append(f"━━━━━━━━━━━━━━━━━━")
    lines.append("I would like to receive a formal quotation and discuss next steps. Thank you!")

    return "\n".join(lines)


def build_whatsapp_link(phone: str, enquiry, brand_name: str = "ApexCraft") -> str:
    cleaned_phone = clean_phone_number(phone)
    message = generate_whatsapp_message(enquiry, brand_name)
    encoded_message = urllib.parse.quote(message)
    if cleaned_phone:
        return f"https://wa.me/{cleaned_phone}?text={encoded_message}"
    return f"https://api.whatsapp.com/send?text={encoded_message}"
