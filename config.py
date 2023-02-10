import os
from dotenv import load_dotenv
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
    DEBUG = True


class ProductionConfig(Config):
    """Devolopment configuration class"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("PROD_SQLALCHEMY_DATABASE_URI")
    pass


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
