from flask import Flask, session, g
from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registrar blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.chaves import bp as chaves_bp
    app.register_blueprint(chaves_bp)

    # User loader
    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    # Verificar token de sessão a cada request
    from flask_login import current_user, logout_user
    from app.models import SessaoAtiva
    from datetime import datetime

    @app.before_request
    def verificar_token_sessao():
        from flask import request
        # Ignorar rotas estáticas e públicas
        public_endpoints = {'auth.login', 'auth.registrar', 'static'}
        if request.endpoint in public_endpoints:
            return

        if current_user.is_authenticated:
            token = session.get('auth_token')
            if not token:
                logout_user()
                return

            sessao = SessaoAtiva.query.filter_by(token_sessao=token).first()
            if not sessao or sessao.is_expired:
                logout_user()
                session.pop('auth_token', None)
                return

            # Atualizar último acesso (a cada 60s para não sobrecarregar o DB)
            from datetime import timedelta
            if not sessao.ultimo_acesso or \
               (datetime.utcnow() - sessao.ultimo_acesso).total_seconds() > 60:
                sessao.ultimo_acesso = datetime.utcnow()
                db.session.commit()

    # Rota raiz → redireciona para painel
    @app.route('/')
    def root():
        from flask import redirect, url_for
        return redirect(url_for('chaves.index'))

    # Rota de setup inicial
    @app.route('/setup')
    def setup():
        from werkzeug.security import generate_password_hash
        db.create_all()
        if not Usuario.query.filter_by(email='admin@escola.com').first():
            admin = Usuario(
                nome='Administrador',
                email='admin@escola.com',
                senha_hash=generate_password_hash('Admin@123'),
                tipo='Admin',
                is_active=True
            )
            user = Usuario(
                nome='João Silva',
                email='joao@escola.com',
                senha_hash=generate_password_hash('Joao@123'),
                tipo='Comum',
                is_active=True
            )
            db.session.add_all([admin, user])

        from app.models import Chave
        if not Chave.query.first():
            chaves = [
                Chave(nome='Sala 101',   status='Disponivel'),
                Chave(nome='Lab Info',   status='Disponivel'),
                Chave(nome='Auditório',  status='Disponivel'),
            ]
            db.session.add_all(chaves)

        db.session.commit()
        from flask import jsonify
        return (
            '<h2>✅ Banco criado com sucesso!</h2>'
            '<p>Admin: admin@escola.com / Admin@123</p>'
            '<p>Comum: joao@escola.com / Joao@123</p>'
            '<p><a href="/">Ir para o sistema</a></p>'
        )

    return app
