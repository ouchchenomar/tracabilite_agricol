import os
from datetime import timedelta

class Config:
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tracabilite_agricole.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration de sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # Configuration du serveur
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 8050

    # Configuration du cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Configuration des logs
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'dashboard.log'

    CONTRACT_ADDRESS = '0x480608b80112000Fd2854EfDb37Bd2e4CbE29F92'
    WEB3_PROVIDER = 'http://localhost:7545'  # URL de Ganache