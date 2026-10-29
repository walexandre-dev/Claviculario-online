from tests.conftest import login


def test_retirar_e_devolver_chave_fluxo_usuario_comum(client, usuario_ativo, chave):
    login(client, 'ativo@escola.com', 'Senha@123')

    resp = client.post(f'/retirar/{chave.id}', follow_redirects=True)
    assert resp.status_code == 200
    assert chave.status == 'Em Uso'

    resp = client.post(f'/devolver/{chave.id}', follow_redirects=True)
    assert resp.status_code == 200
    # Usuário comum não confirma a devolução sozinho: fica "Pendente"
    assert chave.status == 'Pendente'


def test_admin_confirma_devolucao(client, admin_user, chave, db):
    from app.models import Movimentacao

    chave.status = 'Pendente'
    db.session.add(Movimentacao(chave_id=chave.id, usuario_nome='Alguém'))
    db.session.commit()

    login(client, 'admin@escola.com', 'Admin@123')
    resp = client.post(f'/confirmar/{chave.id}', follow_redirects=True)
    assert resp.status_code == 200
    assert chave.status == 'Disponivel'


def test_usuario_pendente_nao_acessa_painel(client, usuario_pendente):
    login(client, 'pendente@escola.com', 'Senha@123')
    resp = client.get('/painel', follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/auth/aguardando-aprovacao'


def test_usuario_comum_nao_pode_excluir_chave(client, usuario_ativo, chave):
    login(client, 'ativo@escola.com', 'Senha@123')
    resp = client.post(f'/chaves/excluir/{chave.id}', follow_redirects=True)
    assert resp.status_code == 200
    from app.extensions import db
    from app.models import Chave
    assert db.session.get(Chave, chave.id) is not None
