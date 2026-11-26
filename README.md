# Website Sales Catalogue & Client Acquisition Platform

A high-converting, standalone website sales catalogue and digital showroom designed specifically to showcase approved website designs, demonstrate real interactive functionality, and convert prospective business owners into paying website development clients.

> **Key Distinction:** This platform is a **commercial website showroom and client acquisition engine**, *not* a personal developer portfolio. Every interaction, package card, showcase preview, and inquiry workflow is tailored to establish credibility, demonstrate value, and generate qualified sales leads with automated WhatsApp routing.

---

## 🌟 Primary Features & Capabilities

### 1. Public Showroom & Discovery
- **Homepage (10 Structured Sections):**
  1. Sticky navigation with configurable logo and branding.
  2. High-impact hero section: *"Your Business Deserves More Than Just a Social Media Page."*
  3. Featured website showcases with category tags, intended business niche, and quick links.
  4. Visual category chips with live project counts.
  5. Value proposition: *6 Critical Reasons to get a professional website vs relying on social media*.
  6. 4-step client journey (*Explore Concept → Choose Package & Add-ons → Customisation & Build → Launch & Sell*).
  7. Transparent package overview with prices in Nigerian Naira (₦).
  8. Interactive FAQ accordion answering common business owner questions.
  9. Final high-conversion enquiry call to action.
  10. Comprehensive footer with direct WhatsApp, phone, email, office address, and social links.

- **Catalogue & Search:**
  - Full-text search across titles, industries, and descriptions.
  - Category filtering by industry (Fashion, Electronics, Furniture, Automotive, E-commerce, Corporate, Web Apps).
  - Sort by Featured First, Newest, Most Popular (page views), or Alphabetical.
  - Dedicated badges for featured showcases.

- **Interactive Showcase Detail & Responsive Device Viewport:**
  - Viewport switcher: Toggle between **Desktop**, **Tablet (iPad)**, and **Mobile (iPhone)** device frames.
  - Additional screenshot gallery thumbnail viewer.
  - Intended business niche and feature checklist.
  - Available customisations breakdown.
  - "Get a Website Like This" primary CTA that pre-fills the enquiry workflow.

- **Live Demonstration Mode:**
  - Dedicated interactive demo preview frame (`/preview/<slug>`) with a top controls bar, viewport switcher, external direct link, and quick inquiry button.

- **Packages & Customisation Add-on Calculator:**
  - Transparent pricing in Nigerian Naira (₦) for **Basic**, **Standard**, **Premium**, and **Custom** tiers.
  - Interactive add-on selection checklist with real-time price estimation (₦) for payment gateways, shopping carts, WhatsApp ordering, user accounts, and booking engines.

- **Enquiry & WhatsApp Client Acquisition Workflow:**
  - Comprehensive intake form: Full Name, Business Name, WhatsApp Number, Email, Selected Concept, Selected Package, Selected Add-ons, Requirements brief, and Budget Range.
  - Automated project estimate calculation in ₦ with clear confirmation disclaimer.
  - Unique enquiry reference code generation (e.g. `ENQ-2026-XXXX`).
  - Instant redirection to confirmation screen with a pre-formatted click-to-chat WhatsApp button:
    ```
    👋 *New Website Enquiry - ApexCraft Studios*
    📋 *Reference:* #ENQ-2026-XXXX
    👤 *Client Name:* Emeka Adeleke
    🏢 *Business:* Luxe Atelier
    📞 *WhatsApp:* +2348012345678
    🌐 *Interested Design:* Aura Atelier Luxury Fashion
    📦 *Selected Package:* Standard E-commerce (₦250,000)
    ⚡ *Selected Add-Ons:* Online Payment Integration
    💰 *Estimated Total:* ₦285,000 (Subject to confirmation)
    ```

---

### 2. Comprehensive Administrator Dashboard

Administrators can manage every aspect of the platform without editing source code:
- **Dashboard Overview:**
  - Published vs draft project counts.
  - Total inquiries, new pending inquiries, won deals, and conversion rate metric.
  - Most viewed showcases (with view-count tracking).
  - Showroom category demand analytics.
  - Recent inquiries feed.
- **Website Management:** Add, edit, delete, upload multiple screenshots, toggle publish/draft status, feature on homepage, configure features list and live demo URLs.
- **Category Management:** Create, rename, reorder, and activate/deactivate categories.
- **Package Management:** Create packages, adjust pricing in ₦, manage included/excluded feature lists, set recommended badges, and reorder tiers.
- **Add-on Management:** Create customisation options, set optional pricing, and toggle active status.
- **Enquiry Management:**
  - Filter inquiries by status: `New`, `Contacted`, `Quotation Sent`, `Negotiating`, `Won`, `Lost`.
  - Review prospect brief, selected add-ons, and calculated estimate.
  - Update deal statuses with automated audit logs.
  - Add internal notes and follow-up timeline entries.
  - One-click "Chat with Client on WhatsApp" direct link.
- **Site & Brand Settings:**
  - Update Brand Name, Tagline, Hero Title & Subtitle, WhatsApp business number, contact phone, contact email, office address, and social links instantly.

---

## 🎨 Visual Design Direction

Built according to the PRD's light, premium design language:
- **Palette:**
  - Background: Warm off-white (`#FAF8F5`) and crisp card surfaces (`#FFFFFF`).
  - Typography: Deep warm charcoal (`#1C1917`, `#292524`).
  - Accents: Muted gold / restrained brass (`#B8860B`, `#C59B27`) and soft cream (`#F4EFE6`).
- **Typography:** Google Fonts `Outfit` (display/headings) & `Plus Jakarta Sans` (body).
- **Cards & Structure:** Subtle border outlines (`#E7E3DC`), soft elevation shadows, consistent rounded corners (`14px` - `20px`), and responsive grid layouts.

---

## 🛠️ Technical Architecture

- **Backend:** Python 3.13, Flask 3.1.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.
- **Authentication & Security:** Flask-Login, Flask-WTF CSRF protection, Werkzeug password hashing, secure file upload validation.
- **Database:** PostgreSQL (Supabase / Render production) or SQLite (local development).
- **Persistent Storage:** Local static uploads with UUID naming, plus built-in Cloudinary integration for persistent cloud image storage.
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, responsive CSS mockups, vanilla JavaScript.

---

## 🚀 Getting Started Locally

### 1. Clone & Set Up Virtual Environment
```bash
git clone <repository-url>
cd "catalogue website"

# Create virtual environment
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Configure parameters in `.env`:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secure-random-key
DATABASE_URL=sqlite:///catalogue.db

# Default Admin Credentials
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@catalogue.com
ADMIN_PASSWORD=AdminSecure2026!
```

### 3. Initialize & Seed Database
```bash
python run.py seed-db
```
*This seeds the database with the default admin account, all 7 categories, initial packages (Basic, Standard, Premium, Custom), add-ons, configurable branding, and 7 realistic website showcase concepts.*

### 4. Run Development Server
```bash
python run.py
```
Open your browser at:
- **Public Showroom:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Dashboard:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
  - **Username:** `admin` (or `admin@catalogue.com`)
  - **Password:** `AdminSecure2026!`

---

## 🧪 Automated Testing

Run the full pytest suite:
```bash
python -m pytest -v
```
All 6 comprehensive test suites cover:
1. Public route rendering and layout integration.
2. Search, category filtering, and sorting.
3. Showcase details, responsive device switcher, and live demo frames.
4. Enquiry submission, automated estimate calculation, and WhatsApp message generation.
5. Admin authentication, login protection, and session handling.
6. Admin CRUD operations (websites, categories, packages, add-ons, enquiry statuses, and site branding settings).

---

## ☁️ Deployment Guide (Render & Supabase)

### Deploying to Render
1. Push this repository to GitHub or GitLab.
2. Log into [Render](https://render.com) and click **New +** → **Blueprint**.
3. Select your repository. Render will automatically detect `render.yaml`.
4. Configure the environment variables:
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string (e.g. `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`).
   - `SECRET_KEY`: A strong random string.
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: (Optional) For persistent cloud image storage.
5. Click **Apply**. The web service will build using `pip install -r requirements.txt` and start with `gunicorn run:app`.

---

## 📁 Repository Structure

```
catalogue_website/
├── app/
│   ├── __init__.py               # Flask app factory, error handlers, Jinja filters
│   ├── config.py                 # Environment-based config & PostgreSQL URL normalizer
│   ├── extensions.py             # SQLAlchemy, Migrate, LoginManager, CSRFProtect
│   ├── models/                   # Modular database models
│   │   ├── user.py               # AdminUser with password hashing & UserMixin
│   │   ├── category.py           # WebsiteCategory with project relationship
│   │   ├── project.py            # WebsiteProject, WebsiteImage, ProjectFeature
│   │   ├── package.py            # Package and PackageFeature (₦ pricing)
│   │   ├── addon.py              # AddOn model
│   │   ├── enquiry.py            # Enquiry, EnquiryAddOn, EnquiryNote
│   │   ├── analytics.py          # WebsiteView tracking
│   │   └── settings.py           # SiteSetting (dynamic brand settings)
│   ├── blueprints/
│   │   ├── public/               # Public routes (Home, Catalogue, Details, Preview, Contact)
│   │   ├── admin/                # Admin auth, dashboard, and CRUD routes & WTForms
│   │   └── api/                  # JSON API for live search & estimate calculation
│   ├── services/
│   │   ├── storage.py            # Image file uploads (local & Cloudinary)
│   │   ├── whatsapp.py           # Phone normalization & WhatsApp message builder
│   │   └── analytics_service.py  # Page views & dashboard metrics compilation
│   ├── static/
│   │   ├── css/custom.css        # Warm light palette, device frames, responsive styles
│   │   └── js/
│   │       ├── main.js           # Device frame switcher & UI utilities
│   │       └── enquiry.js        # Dynamic add-on estimate calculator
│   └── templates/
│       ├── base.html             # Master layout with navbar, flash messages, footer
│       ├── public/               # Public templates (index, catalogue, showcase, etc.)
│       └── admin/                # Admin templates (dashboard, websites, packages, etc.)
├── seeds/
│   └── seed_data.py              # Initial database population script
├── tests/
│   └── test_app.py               # Automated pytest test suite
├── .env.example                  # Environment template
├── Procfile                      # Render / Heroku process declaration
├── render.yaml                   # Render Blueprint infrastructure definition
├── requirements.txt              # Production dependencies
├── run.py                        # Entrypoint and CLI commands
└── README.md                     # Documentation
```
