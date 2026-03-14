import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'claviculario_enterprise_secret_v3_2024!')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///banco_v3.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_TOKEN_EXPIRY_DAYS = 30
    # Máximo de sessões simultâneas por usuário
    MAX_SESSOES_POR_USUARIO = 10
