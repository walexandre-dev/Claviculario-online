import re
import secrets
from datetime import datetime

from flask import (
    render_template, request, redirect, url_for,
    flash, session, current_app
)
from flask_login import (
    login_user, login_required, logout_user, current_user
)

from app.auth import bp
from app.extensions import db
from app.models import Usuario, SessaoAtiva

# ─── Helpers ───────────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
SENHA_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$')  # mín 8 chars, letra + número


def _get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()


def _get_dispositivo():
    ua = request.user_agent
    browser = ua.browser or 'Navegador desconhecido'
    platform = ua.platform or 'Plataforma desconhecida'
    browser = browser.capitalize()
    platform = platform.capitalize()
    return f'{browser} em {platform}'


def _criar_sessao(usuario):
    """Cria um token de sessão, salva no DB e na sessão Flask."""
    token = secrets.token_hex(32)
    sessao = SessaoAtiva(
        usuario_id=usuario.id,
        token_sessao=token,
        ip_address=_get_ip(),
        dispositivo=_get_dispositivo(),
        criado_em=datetime.utcnow(),
        ultimo_acesso=datetime.utcnow()
    )
    db.session.add(sessao)

    # Limpar sessões expiradas do usuário
    _limpar_sessoes_expiradas(usuario.id)

    # Limitar número máximo de sessões
    max_sessoes = current_app.config.get('MAX_SESSOES_POR_USUARIO', 10)
    sessoes_ativas = SessaoAtiva.query.filter_by(usuario_id=usuario.id)\
        .order_by(SessaoAtiva.ultimo_acesso.asc()).all()

    if len(sessoes_ativas) >= max_sessoes:
        # Remove a mais antiga
        db.session.delete(sessoes_ativas[0])

    db.session.commit()
    session['auth_token'] = token
    session.permanent = True
    return token


def _limpar_sessoes_expiradas(usuario_id):
    from datetime import datetime
    SessaoAtiva.query.filter(
        SessaoAtiva.usuario_id == usuario_id,
        SessaoAtiva.expira_em < datetime.utcnow()
    ).delete()


# ─── Rotas ────────────────────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chaves.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        user = Usuario.query.filter_by(email=email).first()

        if not user or not user.check_password(senha):
            flash('E-mail ou senha incorretos. Tente novamente.', 'danger')
            return render_template('auth/login.html')

        if user.is_banned:
            flash('Sua conta foi banida. Entre em contato com o administrador.', 'danger')
            return render_template('auth/login.html')

        # Login bem-sucedido — mesmo sem aprovação (redireciona para aguardando)
        login_user(user, remember=True)
        _criar_sessao(user)

        if not user.is_active:
            return redirect(url_for('auth.aguardando_aprovacao'))

        flash(f'Bem-vindo de volta, {user.nome.split()[0]}! 👋', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('chaves.index'))

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    # Revogar apenas este token
    token = session.get('auth_token')
    if token:
        sessao = SessaoAtiva.query.filter_by(token_sessao=token).first()
        if sessao:
            db.session.delete(sessao)
            db.session.commit()
    session.pop('auth_token', None)
    logout_user()
    flash('Sessão encerrada com segurança. Até logo! 🔒', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('chaves.index'))

    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        conf  = request.form.get('confirmar_senha', '')

        erros = []

        if not nome or len(nome) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres.')

        if not EMAIL_RE.match(email):
            erros.append('Formato de e-mail inválido.')
        elif Usuario.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado.')

        if not SENHA_RE.match(senha):
            erros.append('Senha deve ter mínimo 8 caracteres com letras e números.')

        if senha != conf:
            erros.append('As senhas não coincidem.')

        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('auth/registrar.html',
                                   nome=nome, email=email)

        novo = Usuario(
            nome=nome,
            email=email,
            tipo='Comum',
            is_active=False  # Aguarda aprovação do admin
        )
        novo.set_password(senha)
        db.session.add(novo)
        db.session.commit()

        flash('Cadastro realizado! Aguarde a aprovação do administrador.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registrar.html')


@bp.route('/aguardando-aprovacao')
@login_required
def aguardando_aprovacao():
    if current_user.is_active:
        return redirect(url_for('chaves.index'))
    return render_template('auth/aguardando_aprovacao.html')


@bp.route('/minhas-sessoes')
@login_required
def minhas_sessoes():
    if not current_user.is_active:
        return redirect(url_for('auth.aguardando_aprovacao'))

    token_atual = session.get('auth_token')
    sessoes = SessaoAtiva.query.filter_by(usuario_id=current_user.id)\
        .order_by(SessaoAtiva.ultimo_acesso.desc()).all()

    return render_template(
        'auth/minhas_sessoes.html',
        sessoes=sessoes,
        token_atual=token_atual
    )


@bp.route('/revogar-sessao/<int:sessao_id>', methods=['POST'])
@login_required
def revogar_sessao(sessao_id):
    sessao = SessaoAtiva.query.get_or_404(sessao_id)

    # Garantir que o usuário só pode revogar as próprias sessões
    if sessao.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('auth.minhas_sessoes'))

    token_atual = session.get('auth_token')
    if sessao.token_sessao == token_atual:
        flash('Você não pode revogar a sessão atual por aqui. Use "Sair".', 'warning')
        return redirect(url_for('auth.minhas_sessoes'))

    db.session.delete(sessao)
    db.session.commit()
    flash('Sessão revogada com sucesso.', 'success')
    return redirect(url_for('auth.minhas_sessoes'))


@bp.route('/revogar-todas-outras', methods=['POST'])
@login_required
def revogar_todas_outras():
    token_atual = session.get('auth_token')
    SessaoAtiva.query.filter(
        SessaoAtiva.usuario_id == current_user.id,
        SessaoAtiva.token_sessao != token_atual
    ).delete()
    db.session.commit()
    flash('Todos os outros dispositivos foram desconectados.', 'success')
    return redirect(url_for('auth.minhas_sessoes'))
