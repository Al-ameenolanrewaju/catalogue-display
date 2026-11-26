from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, 
    TextAreaField, DecimalField, IntegerField, SelectField
)
from wtforms.validators import DataRequired, Email, Length, Optional, URL, NumberRange


class LoginForm(FlaskForm):
    identity = StringField('Username or Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    display_order = IntegerField('Display Order', default=0, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Category')


class WebsiteProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=150)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    intended_business_type = StringField('Intended Business Type', validators=[DataRequired(), Length(max=150)], 
                                         description='e.g., Luxury Boutique, Electronics Retailer, Law Firm')
    short_description = StringField('Short Description', validators=[DataRequired(), Length(max=255)])
    full_description = TextAreaField('Detailed Description', validators=[DataRequired()])
    live_demo_url = StringField('Live Demo URL', validators=[Optional(), URL()])
    features = TextAreaField('Included Features (one per line)', validators=[Optional()],
                             description='e.g., WhatsApp Ordering\nAutomated Inventory\nMobile Responsive')
    primary_image_file = FileField('Upload Primary Screenshot', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'svg'], 'Images only!')
    ])
    primary_image_url = StringField('Or Primary Image URL', validators=[Optional(), URL()],
                                    description='Unsplash or external image URL')
    gallery_image_urls = TextAreaField('Additional Gallery Image URLs (one per line)', validators=[Optional()])
    is_featured = BooleanField('Featured on Homepage', default=False)
    is_published = BooleanField('Published (Visible to Visitors)', default=True)
    submit = SubmitField('Save Project')


class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=100)])
    slug = StringField('Package Identifier / Slug', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price (NGN ₦)', places=2, validators=[Optional(), NumberRange(min=0)], 
                         description='Leave empty or set to 0 for Custom Quote')
    is_recommended = BooleanField('Mark as Recommended / Popular', default=False)
    display_order = IntegerField('Display Order', default=0)
    is_active = BooleanField('Active', default=True)
    features = TextAreaField('Package Features (one per line, prefix with "-" to mark as excluded)', 
                            validators=[Optional()],
                            description='e.g., 5 Responsive Pages\nFree .com.ng Domain\nWhatsApp Chat\n- Custom Mobile App')
    submit = SubmitField('Save Package')


class AddOnForm(FlaskForm):
    name = StringField('Add-on Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Optional Price (NGN ₦)', places=2, validators=[Optional(), NumberRange(min=0)],
                         description='Leave empty for quotation upon request')
    display_order = IntegerField('Display Order', default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Add-on')


class EnquiryStatusForm(FlaskForm):
    status = SelectField('Update Status', validators=[DataRequired()])
    submit = SubmitField('Update')


class EnquiryNoteForm(FlaskForm):
    note_text = TextAreaField('Add Internal Note', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Add Note')


class SiteSettingsForm(FlaskForm):
    brand_name = StringField('Brand Name', validators=[DataRequired(), Length(max=100)])
    brand_tagline = StringField('Tagline', validators=[Optional(), Length(max=255)])
    hero_title = StringField('Homepage Hero Title', validators=[DataRequired(), Length(max=255)])
    hero_subtitle = TextAreaField('Homepage Hero Subtitle', validators=[DataRequired()])
    whatsapp_number = StringField('WhatsApp Business Number (with country code)', validators=[DataRequired(), Length(max=50)])
    contact_phone = StringField('Phone Number', validators=[Optional(), Length(max=50)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=120)])
    office_address = StringField('Office / City Address', validators=[Optional(), Length(max=255)])
    currency_symbol = StringField('Currency Symbol', default='₦', validators=[DataRequired(), Length(max=10)])
    instagram_url = StringField('Instagram URL', validators=[Optional(), URL()])
    twitter_url = StringField('X / Twitter URL', validators=[Optional(), URL()])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    facebook_url = StringField('Facebook URL', validators=[Optional(), URL()])
    submit = SubmitField('Save Settings')
