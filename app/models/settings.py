from datetime import datetime, timezone
from app.extensions import db


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'

    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        setting = db.session.get(cls, key)
        if setting and setting.value is not None:
            return setting.value
        return default

    @classmethod
    def set(cls, key: str, value: str, description: str = None):
        setting = db.session.get(cls, key)
        if not setting:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        else:
            setting.value = value
            if description:
                setting.description = description
        db.session.commit()
        return setting

    def __repr__(self):
        return f'<SiteSetting {self.key}={self.value}>'
