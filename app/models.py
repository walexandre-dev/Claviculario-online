from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
from app.extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    tipo       = db.Column(db.String(20), default='Comum')
    is_active  = db.Column(db.Boolean, default=False)
    is_banned  = db.Column(db.Boolean, default=False)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow)

    sessoes = db.relationship(
        'SessaoAtiva',
        backref='usuario',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, senha):
        from werkzeug.security import generate_password_hash
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        return self.tipo == 'Admin'

    # Flask-Login usa is_active para verificar se conta está habilitada
    # Sobrescrevemos para retornar True sempre (usamos is_active/is_banned separadamente)
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Chave(db.Model):
    __tablename__ = 'chave'

    id     = db.Column(db.Integer, primary_key=True)
    nome   = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Disponivel')

    movimentacoes = db.relationship(
        'Movimentacao',
        backref='chave',
        lazy=True
    )

    def __repr__(self):
        return f'<Chave {self.nome}>'


class Movimentacao(db.Model):
    __tablename__ = 'movimentacao'

    id            = db.Column(db.Integer, primary_key=True)
    chave_id      = db.Column(db.Integer, db.ForeignKey('chave.id'))
    usuario_nome  = db.Column(db.String(100))
    data_retirada = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Movimentacao chave={self.chave_id}>'


class SessaoAtiva(db.Model):
    __tablename__ = 'sessao_ativa'

    id            = db.Column(db.Integer, primary_key=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    token_sessao  = db.Column(db.String(128), unique=True, nullable=False)
    ip_address    = db.Column(db.String(50))
    dispositivo   = db.Column(db.String(300))
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    expira_em     = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token_sessao:
            self.token_sessao = secrets.token_hex(32)
        if not self.expira_em:
            self.expira_em = datetime.utcnow() + timedelta(days=30)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expira_em

    @property
    def esta_ativo_agora(self):
        if not self.ultimo_acesso:
            return False
        delta = datetime.utcnow() - self.ultimo_acesso
        return delta.total_seconds() < 300  # 5 minutos

    @property
    def tempo_desde_acesso(self):
        if not self.ultimo_acesso:
            return 'Desconhecido'
        delta = datetime.utcnow() - self.ultimo_acesso
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return 'Agora mesmo'
        elif seconds < 3600:
            return f'Há {seconds // 60} min'
        elif seconds < 86400:
            return f'Há {seconds // 3600}h'
        else:
            return f'Há {seconds // 86400}d'

    def __repr__(self):
        return f'<SessaoAtiva user={self.usuario_id} ip={self.ip_address}>'
