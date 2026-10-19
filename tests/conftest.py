import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Chave, Usuario
from config import TestConfig


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def admin_user(db):
    user = Usuario(
        nome='Administrador',
        email='admin@escola.com',
        tipo='Admin',
        aprovado=True,
    )
    user.set_password('Admin@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def usuario_pendente(db):
    user = Usuario(
        nome='Usuário Pendente',
        email='pendente@escola.com',
        tipo='Comum',
        aprovado=False,
    )
    user.set_password('Senha@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def usuario_ativo(db):
    user = Usuario(
        nome='Usuário Ativo',
        email='ativo@escola.com',
        tipo='Comum',
        aprovado=True,
    )
    user.set_password('Senha@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def chave(db):
    chave = Chave(nome='Sala 101', status='Disponivel')
    db.session.add(chave)
    db.session.commit()
    return chave


def login(client, email, senha):
    return client.post(
        '/auth/login',
        data={'email': email, 'senha': senha},
        follow_redirects=False,
    )
