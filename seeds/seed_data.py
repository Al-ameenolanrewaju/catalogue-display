import os
from app.extensions import db
from app.models import (
    AdminUser, WebsiteCategory, WebsiteProject, WebsiteImage, 
    ProjectFeature, Package, PackageFeature, AddOn, SiteSetting
)


def seed_database():
    """Populates initial database content according to the PRD."""
    
    # 1. Admin User
    admin_user = AdminUser.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = AdminUser(
            username=os.environ.get('ADMIN_USERNAME', 'admin'),
            email=os.environ.get('ADMIN_EMAIL', 'admin@catalogue.com')
        )
        admin_user.set_password(os.environ.get('ADMIN_PASSWORD', 'AdminSecure2026!'))
        db.session.add(admin_user)
        print("Created default admin user.")

    # 2. Site Settings (Brand identity)
    default_settings = [
        ('brand_name', 'ApexCraft Studios', 'Configurable Brand Name'),
        ('brand_tagline', 'Turn Browsers Into Buyers With High-Converting Websites', 'Brand Tagline'),
        ('hero_title', 'Your Business Deserves More Than Just a Social Media Page.', 'Hero Main Headline'),
        ('hero_subtitle', 'Professional websites designed to help Nigerian and global businesses showcase products, build rock-solid credibility, and generate paying customers 24/7.', 'Hero Supporting Copy'),
        ('whatsapp_number', '2348039281144', 'Main Business WhatsApp for Direct Inquiries'),
        ('contact_phone', '+234 803 928 1144', 'Public Phone Number'),
        ('contact_email', 'hello@apexcraft.ng', 'Public Contact Email'),
        ('office_address', 'Admiralty Way, Lekki Phase 1, Lagos, Nigeria', 'Office / City Location'),
        ('currency_symbol', '₦', 'Default Currency Symbol'),
        ('instagram_url', 'https://instagram.com', 'Instagram Profile'),
        ('twitter_url', 'https://twitter.com', 'X / Twitter Profile'),
        ('linkedin_url', 'https://linkedin.com', 'LinkedIn Profile'),
        ('facebook_url', 'https://facebook.com', 'Facebook Page')
    ]
    for key, val, desc in default_settings:
        if not db.session.get(SiteSetting, key):
            s = SiteSetting(key=key, value=val, description=desc)
            db.session.add(s)

    # 3. Categories
    categories_data = [
        ('Fashion and Clothing', 'fashion-and-clothing', 'Apparel, footwear, bespoke tailoring, and luxury accessory boutiques.', 1),
        ('Electronics and Gadgets', 'electronics-and-gadgets', 'Smartphones, audio gear, computer hardware, and smart appliances.', 2),
        ('Furniture', 'furniture', 'Modern home decor, office furnishings, interior woodwork, and architectural living.', 3),
        ('Automotive', 'automotive', 'Car dealerships, auto spare parts, vehicle diagnostics, and fleet leasing.', 4),
        ('General E-commerce', 'general-e-commerce', 'Multi-department retail stores, supermarkets, and general merchandise.', 5),
        ('Business Websites', 'business-websites', 'Corporate firms, legal practices, consulting agencies, and professional services.', 6),
        ('Custom Web Applications', 'custom-web-applications', 'SaaS platforms, logistics management, client portals, and bespoke workflow tools.', 7),
    ]
    category_map = {}
    for name, slug, desc, order in categories_data:
        cat = WebsiteCategory.query.filter_by(slug=slug).first()
        if not cat:
            cat = WebsiteCategory(name=name, slug=slug, description=desc, display_order=order, is_active=True)
            db.session.add(cat)
            db.session.flush()
        category_map[slug] = cat

    # 4. Packages
    packages_data = [
        {
            'name': 'Basic Website',
            'slug': 'basic',
            'description': 'Ideal for emerging businesses seeking a clean online presence, mobile-friendly landing pages, and instant WhatsApp inquiry routing.',
            'price': 120000.0,
            'is_recommended': False,
            'display_order': 1,
            'features': [
                ('1 to 3 Custom Crafted Pages', True),
                ('Mobile & Tablet Responsive Design', True),
                ('Direct WhatsApp Chat & Lead Form', True),
                ('Basic Search Engine Optimization (SEO)', True),
                ('Google Business Map Integration', True),
                ('Fast 5-Day Delivery', True),
                ('Online Payment Gateway Integration', False),
                ('Product Catalog & Shopping Cart', False),
                ('Admin Content Management Portal', False),
            ]
        },
        {
            'name': 'Standard E-commerce / Business',
            'slug': 'standard',
            'description': 'The most popular package for growing businesses. Complete product showcase, customer inquiries, payment processing, and admin dashboard.',
            'price': 250000.0,
            'is_recommended': True,
            'display_order': 2,
            'features': [
                ('Up to 8 Custom Designed Pages', True),
                ('Product Showroom / Service Catalog', True),
                ('Online Payment Processing (Paystack / Flutterwave)', True),
                ('Interactive WhatsApp Order Generator', True),
                ('Custom Admin Dashboard to update text & photos', True),
                ('Speed & Mobile Optimization', True),
                ('Comprehensive On-Page SEO & Social Meta', True),
                ('1 Year Domain (.com.ng or .com) & Hosting Guidance', True),
                ('Free 30-Day Post-Launch Support', True),
                ('Multi-Vendor Marketplace Support', False),
            ]
        },
        {
            'name': 'Premium Growth Solution',
            'slug': 'premium',
            'description': 'Comprehensive digital powerhouse for established brands looking to scale sales, automate client bookings, and track analytics.',
            'price': 480000.0,
            'is_recommended': False,
            'display_order': 3,
            'features': [
                ('Unlimited Pages & Dynamic Collections', True),
                ('Full E-commerce with Cart, Checkout & User Accounts', True),
                ('Multi-Currency / Multi-Payment Gateways', True),
                ('Automated Email & WhatsApp Receipts', True),
                ('Inventory Management & Low-Stock Alerts', True),
                ('Advanced Analytics & Sales Conversion Tracking', True),
                ('High-Performance CDN & Cloud Hosting Setup', True),
                ('Interactive 3D/Video Showcase Support', True),
                ('Priority 24/7 Support & 90-Day Maintenance', True),
            ]
        },
        {
            'name': 'Custom Enterprise & Web App',
            'slug': 'custom',
            'description': 'Bespoke web applications, SaaS platforms, custom API integrations, portals, or complex workflow solutions tailored precisely to your company.',
            'price': None,
            'is_recommended': False,
            'display_order': 4,
            'features': [
                ('Bespoke Architectural Scope & Wireframing', True),
                ('Custom Database & Backend API Development', True),
                ('Role-Based Access Control (Admin, Staff, Customer)', True),
                ('Third-Party CRM / ERP / SMS Integrations', True),
                ('Rigorous Security Auditing & Automated Backups', True),
                ('Dedicated Engineering Team & SLA Guarantee', True),
                ('Full Source Code Handover & Training Sessions', True),
            ]
        }
    ]

    for pdata in packages_data:
        pkg = Package.query.filter_by(slug=pdata['slug']).first()
        if not pkg:
            pkg = Package(
                name=pdata['name'],
                slug=pdata['slug'],
                description=pdata['description'],
                price=pdata['price'],
                is_recommended=pdata['is_recommended'],
                display_order=pdata['display_order'],
                is_active=True
            )
            db.session.add(pkg)
            db.session.flush()

            for order, (ftext, finc) in enumerate(pdata['features']):
                pf = PackageFeature(
                    package_id=pkg.id,
                    feature_text=ftext,
                    is_included=finc,
                    display_order=order
                )
                db.session.add(pf)

    # 5. Customisation Add-ons
    addons_data = [
        ('Online Payment Integration', 'Accept Visa, Mastercard, Verve, Bank Transfers, and USSD seamlessly via Paystack or Flutterwave.', 35000.0, 1),
        ('Shopping Cart & Automated Checkout', 'Enable customers to add multiple items to a cart, apply coupon discounts, and calculate delivery fees.', 45000.0, 2),
        ('Customer Accounts & Order Portal', 'Allow customers to register, track order statuses, view download history, and manage shipping addresses.', 40000.0, 3),
        ('WhatsApp Instant Ordering Bot', 'One-click checkout that generates a structured order invoice directly to your business WhatsApp chat.', 25000.0, 4),
        ('Online Booking & Reservation Engine', 'Interactive calendar booking for consultations, test drives, hotel rooms, or appointments with instant confirmation.', 40000.0, 5),
        ('Client Admin Content Dashboard', 'Simple web dashboard allowing your non-technical team to upload new products, change prices, and post updates.', 50000.0, 6),
        ('Advanced Analytics & Sales Conversion Tracking', 'Google Tag Manager, Meta Pixel, and visual weekly sales reporting to see where your customers come from.', 30000.0, 7),
        ('Additional Custom Pages (Batch of 3)', 'Three extra custom designed pages (e.g. Careers, Case Studies, Terms, FAQ, Pricing breakdown).', 25000.0, 8),
        ('Monthly Maintenance & Security Retainer', 'Routine cloud backups, plugin updates, uptime monitoring, and 3 hours of on-demand monthly updates.', 30000.0, 9),
    ]

    for aname, adesc, aprice, aorder in addons_data:
        if not AddOn.query.filter_by(name=aname).first():
            addon = AddOn(
                name=aname,
                description=adesc,
                price=aprice,
                display_order=aorder,
                is_active=True
            )
            db.session.add(addon)

    db.session.commit()

    # 6. Showcase Projects
    projects_data = [
        {
            'title': 'Aura Atelier Luxury Fashion',
            'slug': 'aura-atelier-luxury-fashion',
            'category_slug': 'fashion-and-clothing',
            'intended_business_type': 'High-End Fashion Boutiques & Bespoke Designers',
            'short_description': 'An editorial-grade fashion lookbook and commerce platform crafted with silky smooth typography and instant WhatsApp sizing consultations.',
            'full_description': (
                'Aura Atelier is an exquisite, editorial-grade e-commerce concept designed for high-fashion labels, '
                'bespoke tailors, and couture boutiques. It highlights collections through rich lookbooks, '
                'dynamic fabric zoom previews, interactive sizing calculators, and seamless multi-currency support. '
                'Clients can purchase items directly via automated checkout or request custom measurements over WhatsApp.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/le-arts-luxury-fashion-store-html-template/full_screen_preview/28198886',
            'is_featured': True,
            'features': [
                'Editorial Lookbook Grid with Hover Reveals',
                'Interactive Sizing Guide & Fit Advisor',
                'One-Click WhatsApp Bespoke Order Request',
                'Paystack / Flutterwave Multi-Currency Checkout',
                'Mobile-First Sticky Add-to-Bag Bar',
                'Instagram Feed Live Sync Integration'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1400&q=80', True, 'Main Homepage Hero Showcase'),
                ('https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1200&q=80', False, 'Product Catalog & Filter Grid'),
                ('https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1200&q=80', False, 'Bespoke Measurement Booking Screen')
            ]
        },
        {
            'title': 'VoltGear Pro Gadgets & Electronics',
            'slug': 'voltgear-pro-gadgets',
            'category_slug': 'electronics-and-gadgets',
            'intended_business_type': 'Electronics Wholesalers, Phone Stores & Smart Gadget Retailers',
            'short_description': 'High-performance tech retail showroom featuring interactive spec comparison tables, real-time inventory badges, and rapid checkout.',
            'full_description': (
                'VoltGear is engineered specifically for consumer tech retailers, phone dealers, and audio equipment merchants. '
                'It features an ultra-responsive product comparison matrix, live stock indicators, warranty verification tool, '
                'and streamlined payment processing. Designed to communicate engineering precision and inspire buying confidence.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/techmarket-multivendor-electronics-store/full_screen_preview/19717765',
            'is_featured': True,
            'features': [
                'Side-by-Side Technical Specification Comparison',
                'Instant Live Search with Thumbnail Previews',
                'Device Warranty & Serial Number Check Portal',
                'Low Stock Scarcity Badges to Drive Conversions',
                'Integrated Delivery Cost Calculator by City',
                'Secure Card & Bank Transfer Payments'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1550009158-9ebf69173e03?auto=format&fit=crop&w=1400&q=80', True, 'Modern High-Tech Electronics Storefront'),
                ('https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80', False, 'Audio & Gadgets Product Page'),
                ('https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=1200&q=80', False, 'Smartwatch Detail Specifications')
            ]
        },
        {
            'title': 'NordicLiving Architectural Furniture',
            'slug': 'nordicliving-architectural-furniture',
            'category_slug': 'furniture',
            'intended_business_type': 'Interior Design Studios, Custom Woodworkers & Home Decor Brands',
            'short_description': 'Warm minimalist furniture gallery featuring room-by-room staging, 3D visualization feel, and room dimension quotation estimator.',
            'full_description': (
                'Built for bespoke furniture craftsmen and high-end interior showrooms, NordicLiving presents handcrafted pieces '
                'in warm earthy palettes. It includes room inspiration visualizers, custom upholstery material selectors, '
                'and an interactive quotation builder where prospective interior designers can compile large project purchase orders.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/depot-e-commerce-theme/full_screen_preview/19665575',
            'is_featured': True,
            'features': [
                'Room Visualizer (Living Room, Dining, Executive Office)',
                'Wood Finish & Fabric Texture Swatch Selector',
                'Wholesale Quotation Request & PDF Invoice Builder',
                'Dimensions & Floor-Space Compatibility Diagram',
                'Direct Consultation Booking with Interior Architects',
                'Smooth Scroll Gallery & Mobile Optimized Staging'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1400&q=80', True, 'Living Room Interior Showcase'),
                ('https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80', False, 'Architectural Chair & Table Setup'),
                ('https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=1200&q=80', False, 'Minimalist Office Furniture Staging')
            ]
        },
        {
            'title': 'Velocity Apex Motors & Dealership',
            'slug': 'velocity-apex-motors',
            'category_slug': 'automotive',
            'intended_business_type': 'Car Dealerships, Auto Importers & Fleet Leasing Companies',
            'short_description': 'Prestigious vehicle showroom featuring VIN verification, car finance installment calculators, and test drive booking.',
            'full_description': (
                'Velocity Apex is designed to help auto dealers and importers turn vehicle listings into closed sales. '
                'Features comprehensive mileage, condition, and vehicle history tabs, a live monthly car loan repayment calculator, '
                'and an integrated VIP test drive scheduler linked directly to dealership sales managers.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/motors-car-dealer-dealership-automotive-wordpress-theme/full_screen_preview/13922633',
            'is_featured': True,
            'features': [
                'Detailed Car Specification Sheet (Mileage, Year, Engine)',
                'Real-Time Monthly Auto Loan Repayment Calculator',
                'Instant Test Drive Appointment Scheduler',
                'High-Resolution 360-degree Exterior/Interior Gallery',
                'Direct WhatsApp "Inquire on This Vehicle" Button',
                'Vehicle Trade-In Valuation Appraisal Form'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1400&q=80', True, 'Luxury Sports Car Showroom'),
                ('https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=1200&q=80', False, 'Modern Sedan Vehicle Inspection View'),
                ('https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80', False, 'Dashboard Technology Feature')
            ]
        },
        {
            'title': 'PrimeMarket Multi-Category Retail Hub',
            'slug': 'primemarket-retail-hub',
            'category_slug': 'general-e-commerce',
            'intended_business_type': 'Supermarkets, Department Stores & Multi-Product Merchants',
            'short_description': 'Versatile high-volume e-commerce powerhouse built for speedy transactions, flash deal counters, and bulk purchase logistics.',
            'full_description': (
                'Designed for department stores and high-inventory retail operations. Includes lightning-fast search indexing, '
                'flash sale countdown ribbons, customer reviews with star ratings, promo coupon codes, and multi-hub delivery logistics.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/marketo-ecommerce-multivendor-woocommerce-theme/full_screen_preview/22332158',
            'is_featured': False,
            'features': [
                'Mega Menu with Multi-Level Department Navigation',
                'Flash Sale Limited-Time Countdown Timers',
                'Automated Customer Receipt & Shipping Notifications',
                'Customer Reviews & Verified Buyer Badges',
                'Discount Coupons & Seasonal Promo Engine',
                'Bulk Item Pricing & Wholesale Tiers'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1472851294608-062f824d29cc?auto=format&fit=crop&w=1400&q=80', True, 'General Retail & Marketplace Storefront'),
                ('https://images.unsplash.com/photo-1556742049-0a67c5574f73?auto=format&fit=crop&w=1200&q=80', False, 'Shopping Cart & Point-of-Sale Integration')
            ]
        },
        {
            'title': 'Veritas Advisory & Legal Partners',
            'slug': 'veritas-advisory-partners',
            'category_slug': 'business-websites',
            'intended_business_type': 'Corporate Law Firms, Financial Consultants & Accounting Agencies',
            'short_description': 'Authoritative corporate website communicating trust, verified track records, partner credentials, and private client consultations.',
            'full_description': (
                'Veritas Advisory is built for high-trust professional firms where reputation translates directly to billable clients. '
                'Features dedicated partner biographies, published legal insights and case summaries, confidential client intake forms, '
                'and secure appointment scheduling.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/the-gem-creative-multipurpose-highperformance-wordpress-theme/full_screen_preview/16061685',
            'is_featured': True,
            'features': [
                'Executive Partner Profiles & Practice Area Portfolios',
                'Confidential Client Intake & Consultation Request Form',
                'Case Studies & Proven Client Results Timeline',
                'Articles, Whitepapers & Regulatory Insights Blog',
                'Downloadable Corporate Capability Deck (PDF)',
                'Bilingual & International Jurisdiction Selector'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1400&q=80', True, 'Corporate Headquarters & Glass Architecture'),
                ('https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80', False, 'Executive Boardroom Meeting Room'),
                ('https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=1200&q=80', False, 'Consulting Advisory Discussion')
            ]
        },
        {
            'title': 'LogiPulse Fleet & Supply Chain Portal',
            'slug': 'logipulse-fleet-portal',
            'category_slug': 'custom-web-applications',
            'intended_business_type': 'Logistics Operators, Cargo Carriers & Freight Forwarders',
            'short_description': 'Interactive web application showcasing client consignment tracking, freight rate estimation, and cloud dispatch management.',
            'full_description': (
                'A demonstration of custom web application capabilities. Features live tracking number lookups, '
                'volumetric freight quote calculators, interactive driver dispatch views, and client account portals. '
                'Proof of how bespoke web software can automate complex operational workflows.'
            ),
            'live_demo_url': 'https://preview.themeforest.net/item/cargo-transport-logistics-wordpress-theme/full_screen_preview/11494950',
            'is_featured': False,
            'features': [
                'Live Consignment & Container Tracking Lookup Tool',
                'Volumetric Freight & Weight Calculator',
                'Customer Shipping Portal with Real-Time Waybills',
                'Fleet Availability Map & Route Status',
                'Automated SMS & Email Waybill Alerts',
                'B2B Corporate Account Credit Management'
            ],
            'images': [
                ('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1400&q=80', True, 'Logistics Hub & Freight Terminal'),
                ('https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80', False, 'Container Ship & Global Transport'),
                ('https://images.unsplash.com/photo-1519003722824-194d4455a60c?auto=format&fit=crop&w=1200&q=80', False, 'Fleet Transit on Highway')
            ]
        }
    ]

    for p in projects_data:
        proj = WebsiteProject.query.filter_by(slug=p['slug']).first()
        if not proj:
            cat = category_map.get(p['category_slug'])
            proj = WebsiteProject(
                title=p['title'],
                slug=p['slug'],
                category_id=cat.id if cat else None,
                intended_business_type=p['intended_business_type'],
                short_description=p['short_description'],
                full_description=p['full_description'],
                live_demo_url=p['live_demo_url'],
                is_featured=p['is_featured'],
                is_published=True,
                views_count=24
            )
            db.session.add(proj)
            db.session.flush()

            for order, f_text in enumerate(p['features']):
                feat = ProjectFeature(project_id=proj.id, feature_text=f_text, display_order=order)
                db.session.add(feat)

            for order, (img_url, is_prim, cap) in enumerate(p['images']):
                img = WebsiteImage(
                    project_id=proj.id,
                    image_url=img_url,
                    caption=cap,
                    is_primary=is_prim,
                    display_order=order
                )
                db.session.add(img)

    db.session.commit()
    print("Database successfully populated with rich catalogue seed data.")
