import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()


class Config:
    """Class with common configurations for all applications"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "my secret key"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Devolopment configuration class"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_SQLALCHEMY_DATABASE_URI")
    REMEMBER_COOKIE_DURATION = timedelta(days=365)
    DEBUG = True


class ProductionConfig(Config):
    """Devolopment configuration class"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("PROD_SQLALCHEMY_DATABASE_URI")
    REMEMBER_COOKIE_DURATION = timedelta(days=365)


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
