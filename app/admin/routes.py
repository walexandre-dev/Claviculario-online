from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.admin import bp
from app.extensions import db
from app.models import Usuario, SessaoAtiva


# ─── Decorator admin ──────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_active:
            return redirect(url_for('auth.aguardando_aprovacao'))
        if not current_user.is_admin:
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('chaves.index'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Painel de Usuários ───────────────────────────────────────────────────

@bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    pendentes = Usuario.query.filter_by(is_active=False, is_banned=False)\
        .order_by(Usuario.criado_em.asc()).all()
    ativos = Usuario.query.filter_by(is_active=True, is_banned=False)\
        .order_by(Usuario.criado_em.desc()).all()
    banidos = Usuario.query.filter_by(is_banned=True)\
        .order_by(Usuario.criado_em.desc()).all()

    return render_template(
        'admin/usuarios.html',
        pendentes=pendentes,
        ativos=ativos,
        banidos=banidos
    )


@bp.route('/usuarios/aprovar/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def aprovar_usuario(user_id):
    user = db.session.get(Usuario, user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))
    user.is_active = True
    user.is_banned = False
    db.session.commit()
    flash(f'Usuário "{user.nome}" aprovado com sucesso! ✅', 'success')
    return redirect(url_for('admin.usuarios'))


@bp.route('/usuarios/rejeitar/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def rejeitar_usuario(user_id):
    user = db.session.get(Usuario, user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))
    # Remover sessões e excluir usuário rejeitado
    db.session.delete(user)
    db.session.commit()
    flash(f'Cadastro de "{user.nome}" rejeitado e removido.', 'warning')
    return redirect(url_for('admin.usuarios'))


@bp.route('/usuarios/banir/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def banir_usuario(user_id):
    user = db.session.get(Usuario, user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))
    if user.id == current_user.id:
        flash('Você não pode banir a si mesmo.', 'danger')
        return redirect(url_for('admin.usuarios'))
    user.is_active = False
    user.is_banned = True
    # Revogar todas as sessões
    SessaoAtiva.query.filter_by(usuario_id=user.id).delete()
    db.session.commit()
    flash(f'Usuário "{user.nome}" banido e desconectado. 🚫', 'warning')
    return redirect(url_for('admin.usuarios'))


@bp.route('/usuarios/desbanir/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def desbanir_usuario(user_id):
    user = db.session.get(Usuario, user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))
    user.is_banned = False
    user.is_active = False  # Volta para pendente — admin reaprova
    db.session.commit()
    flash(f'Usuário "{user.nome}" desbanido. Precisa ser reaprovado.', 'info')
    return redirect(url_for('admin.usuarios'))


# ─── Cadastro de Usuário pelo Admin ───────────────────────────────────────

@bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        tipo  = request.form.get('tipo', 'Comum')

        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios.', 'warning')
            return redirect(url_for('admin.novo_usuario'))

        if Usuario.query.filter_by(email=email).first():
            flash('Já existe um usuário com este e-mail.', 'danger')
            return redirect(url_for('admin.novo_usuario'))

        novo = Usuario(nome=nome, email=email, tipo=tipo, is_active=True)
        novo.set_password(senha)
        db.session.add(novo)
        db.session.commit()
        flash(f'Usuário "{nome}" cadastrado e aprovado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))

    return render_template('admin/cadastro_usuario.html')
