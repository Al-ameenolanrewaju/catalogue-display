import io
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.models.settings import SiteSetting


def generate_enquiry_pdf(enquiry) -> io.BytesIO:
    """
    Generates a professional, branded A4 PDF Project Proposal & Quotation
    for a given client Enquiry using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    brand_name = SiteSetting.get('brand_name', 'ApexCraft Studios')
    brand_tagline = SiteSetting.get('brand_tagline', 'Premium Website Showroom & Client Acquisition Platform')
    contact_phone = SiteSetting.get('contact_phone', '+234 800 000 0000')
    contact_email = SiteSetting.get('contact_email', 'hello@apexcraft.ng')
    office_address = SiteSetting.get('office_address', 'Victoria Island, Lagos, Nigeria')
    currency_symbol = SiteSetting.get('currency_symbol', '₦')
    bank_name = SiteSetting.get('bank_name', 'Access Bank / GTBank')
    account_number = SiteSetting.get('account_number', '0123456789')
    account_name = SiteSetting.get('account_name', brand_name)

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor('#171514')
    gold_color = colors.HexColor('#D97706')
    muted_color = colors.HexColor('#57534E')
    light_bg = colors.HexColor('#F8F7F4')
    border_color = colors.HexColor('#E7E3DC')

    brand_title_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )
    tagline_style = ParagraphStyle(
        'BrandTagline',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=muted_color
    )
    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=gold_color,
        alignment=2 # Right
    )
    doc_meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=muted_color,
        alignment=2 # Right
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=primary_color
    )
    body_muted = ParagraphStyle(
        'BodyMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=muted_color
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=primary_color
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_color,
        alignment=2 # Right
    )

    story = []

    # 1. Header Section
    created_date = enquiry.created_at.strftime('%B %d, %Y') if enquiry.created_at else datetime.now(timezone.utc).strftime('%B %d, %Y')
    valid_until = (enquiry.created_at + timedelta(days=14)).strftime('%B %d, %Y') if enquiry.created_at else (datetime.now(timezone.utc) + timedelta(days=14)).strftime('%B %d, %Y')

    header_left = [
        Paragraph(f"<b>{brand_name}</b>", brand_title_style),
        Paragraph(f"{brand_tagline}", tagline_style),
        Paragraph(f"{contact_email} &bull; {contact_phone}", tagline_style),
        Paragraph(f"{office_address}", tagline_style),
    ]

    header_right = [
        Paragraph("PROJECT PROPOSAL &amp; QUOTE", doc_title_style),
        Paragraph(f"<b>Reference:</b> #{enquiry.reference_code}", doc_meta_style),
        Paragraph(f"<b>Date Issued:</b> {created_date}", doc_meta_style),
        Paragraph(f"<b>Valid Until:</b> {valid_until}", doc_meta_style),
        Paragraph(f"<b>Status:</b> {enquiry.status}", doc_meta_style),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[320, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=gold_color, spaceBefore=4, spaceAfter=14))

    # 2. Client Profile & Target Website Concept
    client_info = [
        Paragraph("<b>PREPARED FOR:</b>", section_heading),
        Paragraph(f"<b>Client:</b> {enquiry.full_name}", body_style),
        Paragraph(f"<b>Business:</b> {enquiry.business_name}", body_style),
        Paragraph(f"<b>WhatsApp / Phone:</b> {enquiry.whatsapp_number}", body_style),
        Paragraph(f"<b>Email:</b> {enquiry.email or 'Not provided'}", body_style),
    ]

    project_concept_title = enquiry.website.title if enquiry.website else "Custom Bespoke Website"
    concept_business = enquiry.website.intended_business_type if enquiry.website else "Digital Commerce / Service"
    project_info = [
        Paragraph("<b>TARGET CONCEPT:</b>", section_heading),
        Paragraph(f"<b>Selected Concept:</b> {project_concept_title}", body_style),
        Paragraph(f"<b>Industry Focus:</b> {concept_business}", body_style),
        Paragraph(f"<b>Scope:</b> Turnkey Design, Mobile Optimization &amp; Deployment", body_style),
    ]

    info_table = Table([[client_info, project_info]], colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 0.8, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # 3. Itemized Investment Breakdown Table
    story.append(Paragraph("<b>ITEMIZED INVESTMENT BREAKDOWN</b>", section_heading))

    table_data = [
        [
            Paragraph("Item Description &amp; Scope", table_header),
            Paragraph("Type", table_header),
            Paragraph("Estimated Investment", table_header)
        ]
    ]

    subtotal = 0.0

    # Package item
    if enquiry.package:
        pkg_price = enquiry.package.price or 0.0
        subtotal += pkg_price
        pkg_desc = f"<b>{enquiry.package.name}</b><br/><font color='#57534E'>{enquiry.package.description or 'Core platform infrastructure, responsive layouts, and content setup.'}</font>"
        table_data.append([
            Paragraph(pkg_desc, table_cell),
            Paragraph("Base Package", table_cell),
            Paragraph(f"{currency_symbol}{pkg_price:,.2f}" if pkg_price else "Custom Quote", table_cell_bold)
        ])
    else:
        table_data.append([
            Paragraph("<b>Custom Web Architecture Consultation</b><br/><font color='#57534E'>Tailored project scoping and system design.</font>", table_cell),
            Paragraph("Consultation", table_cell),
            Paragraph("Custom Quote", table_cell_bold)
        ])

    # Add-on items
    for ea in enquiry.addons:
        addon_name = ea.add_on.name if ea.add_on else "Custom Feature"
        addon_desc = ea.add_on.description if ea.add_on and ea.add_on.description else "Custom functional add-on module."
        price = ea.price_at_enquiry or (ea.add_on.price if ea.add_on else 0.0) or 0.0
        subtotal += price
        table_data.append([
            Paragraph(f"<b>Add-on: {addon_name}</b><br/><font color='#57534E'>{addon_desc}</font>", table_cell),
            Paragraph("Module Add-on", table_cell),
            Paragraph(f"{currency_symbol}{price:,.2f}" if price else "Included / Quote", table_cell_bold)
        ])

    # Total row
    table_data.append([
        Paragraph("<b>TOTAL ESTIMATED PROJECT INVESTMENT</b>", table_cell_bold),
        Paragraph("", table_cell),
        Paragraph(f"<b>{currency_symbol}{subtotal:,.2f}</b>", table_cell_bold)
    ])

    items_table = Table(table_data, colWidths=[330, 80, 110])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (0, -1), (-1, -1), light_bg),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 14))

    # 4. Project Notes / Brief
    if enquiry.additional_requirements:
        story.append(Paragraph("<b>CLIENT BRIEF &amp; SPECIAL INSTRUCTIONS:</b>", section_heading))
        brief_p = Paragraph(f"<i>&ldquo;{enquiry.additional_requirements}&rdquo;</i>", body_muted)
        brief_table = Table([[brief_p]], colWidths=[520])
        brief_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(brief_table)
        story.append(Spacer(1, 12))

    # 5. Terms, Payment Milestone & Bank Instructions
    terms_text = [
        Paragraph("<b>DELIVERY &amp; PAYMENT TERMS:</b>", section_heading),
        Paragraph("&bull; <b>Turnaround Time:</b> 5 to 10 business days upon provision of logos, text, and photos.", body_muted),
        Paragraph("&bull; <b>Milestone Schedule:</b> 50% commitment deposit to commence design; remaining 50% upon final staging review and handover of live domain.", body_muted),
        Paragraph("&bull; <b>Handover Deliverables:</b> Live hosted website, SSL certificate, admin dashboard access, and 30 days post-launch support.", body_muted),
    ]

    bank_info = [
        Paragraph("<b>PAYMENT ACCOUNT DETAILS:</b>", section_heading),
        Paragraph(f"<b>Bank:</b> {bank_name}", body_style),
        Paragraph(f"<b>Account Number:</b> {account_number}", body_style),
        Paragraph(f"<b>Account Name:</b> {account_name}", body_style),
        Paragraph(f"<b>Payment Narration:</b> Ref #{enquiry.reference_code}", body_muted),
    ]

    footer_table = Table([[terms_text, bank_info]], colWidths=[310, 210])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 0.8, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(footer_table)
    story.append(Spacer(1, 16))

    # 6. Sign-off / Next Step CTA
    cta_p = Paragraph(
        f"<b>Next Steps:</b> To confirm your project slot and initiate development, reach out directly on WhatsApp at <b>{contact_phone}</b> or reply to your confirmation email quoting Reference <b>#{enquiry.reference_code}</b>.",
        body_style
    )
    story.append(cta_p)

    doc.build(story)
    buffer.seek(0)
    return buffer
