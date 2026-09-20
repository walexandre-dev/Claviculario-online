import os
from datetime import timedelta

from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

load_dotenv()

_DEV_SECRET_KEY = 'dev-only-insecure-secret-key'


def _default_secret_key():
    if os.environ.get('FLASK_DEBUG') == '1':
        return _DEV_SECRET_KEY
    return None


class Config:
    # None fora do modo debug: create_app() falha rápido se SECRET_KEY não
    # vier do ambiente (veja .env.example), em vez de usar uma chave fixa
    # em produção.
    SECRET_KEY = os.environ.get('SECRET_KEY', _default_secret_key())
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///banco_v3.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_TOKEN_EXPIRY_DAYS = 30
    # Máximo de sessões simultâneas por usuário
    MAX_SESSOES_POR_USUARIO = int(os.environ.get('MAX_SESSOES_POR_USUARIO', '10'))

    # Cookies de sessão: HttpOnly sempre; Secure deve ser ativado atrás de HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'


class TestConfig(Config):
    """Configuração usada pela suíte de testes (tests/conftest.py)."""
    SECRET_KEY = 'test-secret-key'
    # StaticPool mantém uma única conexão SQLite viva durante todo o teste;
    # sem isso, cada nova conexão a "sqlite:///:memory:" cria um banco vazio
    # diferente e os dados somem entre requisições.
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': StaticPool,
        'connect_args': {'check_same_thread': False},
    }
    WTF_CSRF_ENABLED = False
    TESTING = True
