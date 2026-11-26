from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please log in to access the administration dashboard.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()
