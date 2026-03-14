from functools import wraps
from datetime import datetime, timedelta

from flask import (
    render_template, request, redirect, url_for, flash,
    make_response
)
from flask_login import login_required, current_user

from app.chaves import bp
from app.extensions import db
from app.models import Chave, Movimentacao


# ─── Decorator: conta ativa ───────────────────────────────────────────────

def active_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_active:
            return redirect(url_for('auth.aguardando_aprovacao'))
        return f(*args, **kwargs)
    return decorated


def fechar_movimentacao(chave_id):
    mov = Movimentacao.query.filter_by(
        chave_id=chave_id, data_devolucao=None
    ).first()
    if mov:
        mov.data_devolucao = datetime.utcnow()


# ─── Dashboard ────────────────────────────────────────────────────────────

@bp.route('/painel')
@login_required
@active_required
def index():
    chaves = Chave.query.all()
    movimentacoes_ativas = {
        m.chave_id: m.usuario_nome
        for m in Movimentacao.query.filter_by(data_devolucao=None).all()
    }

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str    = request.args.get('data_fim')

    query = Movimentacao.query.order_by(Movimentacao.data_retirada.desc())

    tab_ativa = 'chaves'

    if data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_fim    = datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                Movimentacao.data_retirada >= data_inicio,
                Movimentacao.data_retirada < data_fim
            )
            historico = query.all()
            tab_ativa = 'historico'
        except ValueError:
            historico = query.limit(50).all()
    else:
        historico = query.limit(50).all()

    return render_template(
        'chaves/index.html',
        chaves=chaves,
        historico=historico,
        mov_ativas=movimentacoes_ativas,
        usuario=current_user,
        tab_ativa=tab_ativa
    )


# ─── Retirar ──────────────────────────────────────────────────────────────

@bp.route('/retirar/<int:chave_id>', methods=['POST'])
@login_required
@active_required
def retirar(chave_id):
    chave = db.get_or_404(Chave, chave_id)
    if chave.status == 'Disponivel':
        chave.status = 'Em Uso'
        db.session.add(Movimentacao(
            chave_id=chave.id,
            usuario_nome=current_user.nome
        ))
        db.session.commit()
        flash(f'Chave "{chave.nome}" retirada com sucesso! 🗝️', 'success')
    else:
        flash('Esta chave não está disponível.', 'danger')
    return redirect(url_for('chaves.index'))


# ─── Devolver ─────────────────────────────────────────────────────────────

@bp.route('/devolver/<int:chave_id>', methods=['POST'])
@login_required
@active_required
def devolver(chave_id):
    chave = db.get_or_404(Chave, chave_id)
    if chave.status == 'Em Uso':
        if current_user.is_admin:
            chave.status = 'Disponivel'
            fechar_movimentacao(chave.id)
            flash(f'Devolução da chave "{chave.nome}" confirmada. ✅', 'success')
        else:
            chave.status = 'Pendente'
            flash('Devolução registrada. Aguardando confirmação do Admin.', 'warning')
        db.session.commit()
    return redirect(url_for('chaves.index'))


# ─── Confirmar devolução (Admin) ──────────────────────────────────────────

@bp.route('/confirmar/<int:chave_id>', methods=['POST'])
@login_required
@active_required
def confirmar(chave_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('chaves.index'))

    chave = db.get_or_404(Chave, chave_id)
    if chave.status == 'Pendente':
        chave.status = 'Disponivel'
        fechar_movimentacao(chave.id)
        db.session.commit()
        flash(f'Chave "{chave.nome}" confirmada como devolvida. ✅', 'success')
    return redirect(url_for('chaves.index'))


# ─── Cadastrar Chave ──────────────────────────────────────────────────────

@bp.route('/chaves/nova', methods=['GET', 'POST'])
@login_required
@active_required
def nova_chave():
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('chaves.index'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        if not nome:
            flash('O nome da chave é obrigatório.', 'warning')
        else:
            db.session.add(Chave(nome=nome, status='Disponivel'))
            db.session.commit()
            flash(f'Chave "{nome}" cadastrada com sucesso! 🔑', 'success')
            return redirect(url_for('chaves.index'))

    return render_template('chaves/cadastro_chave.html')


# ─── Excluir Chave ────────────────────────────────────────────────────────

@bp.route('/chaves/excluir/<int:chave_id>', methods=['POST'])
@login_required
@active_required
def excluir_chave(chave_id):
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('chaves.index'))

    chave = db.get_or_404(Chave, chave_id)
    if chave.status != 'Disponivel':
        flash('Não é possível excluir uma chave em uso ou pendente.', 'warning')
        return redirect(url_for('chaves.index'))

    try:
        db.session.delete(chave)
        db.session.commit()
        flash(f'Chave "{chave.nome}" excluída com sucesso.', 'success')
    except Exception:
        db.session.rollback()
        flash('Erro ao excluir. Pode haver registros históricos vinculados.', 'danger')

    return redirect(url_for('chaves.index'))


# ─── Exportar PDF ─────────────────────────────────────────────────────────

@bp.route('/exportar-pdf')
@login_required
@active_required
def exportar_pdf():
    try:
        from app.utils.pdf import gerar_relatorio_pdf

        data_inicio_str = request.args.get('data_inicio')
        data_fim_str    = request.args.get('data_fim')
        periodo_texto   = 'Histórico Completo'

        query = Movimentacao.query.order_by(Movimentacao.data_retirada.desc())

        if data_inicio_str and data_fim_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                data_fim    = datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(
                    Movimentacao.data_retirada >= data_inicio,
                    Movimentacao.data_retirada < data_fim
                )
                d_i = datetime.strptime(data_inicio_str, '%Y-%m-%d').strftime('%d/%m/%Y')
                d_f = datetime.strptime(data_fim_str, '%Y-%m-%d').strftime('%d/%m/%Y')
                periodo_texto = f'{d_i} a {d_f}'
            except ValueError:
                pass

        movimentacoes = query.all()
        pdf_bytes, filename = gerar_relatorio_pdf(movimentacoes, periodo_texto)

        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    except Exception as e:
        return str(e), 500
