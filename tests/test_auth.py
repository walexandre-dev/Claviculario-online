from tests.conftest import login


def test_login_com_credenciais_invalidas(client, usuario_ativo):
    resp = login(client, 'ativo@escola.com', 'senha_errada')
    assert resp.status_code == 200
    assert 'incorretos' in resp.get_data(as_text=True)


def test_login_usuario_ativo_redireciona_para_painel(client, usuario_ativo):
    resp = login(client, 'ativo@escola.com', 'Senha@123')
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/painel'


def test_login_usuario_pendente_autentica_e_vai_para_aguardando(client, usuario_pendente):
    # Regressão: Usuario.is_active costumava ser a própria coluna de
    # "aprovado pelo admin". Como UserMixin.is_authenticated depende de
    # is_active, um usuário pendente nunca ficava autenticado de verdade,
    # mesmo após um login "bem-sucedido" — quebrando o redirecionamento
    # para a tela de aprovação pendente.
    resp = login(client, 'pendente@escola.com', 'Senha@123')
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/auth/aguardando-aprovacao'

    resp2 = client.get('/auth/aguardando-aprovacao')
    assert resp2.status_code == 200


def test_login_usuario_banido_e_bloqueado(client, usuario_ativo, db):
    usuario_ativo.is_banned = True
    db.session.commit()

    resp = login(client, 'ativo@escola.com', 'Senha@123')
    assert resp.status_code == 200
    assert 'banida' in resp.get_data(as_text=True)


def test_registrar_usuario_com_senha_fraca(client):
    resp = client.post('/auth/registrar', data={
        'nome': 'Novo Usuário',
        'email': 'novo@escola.com',
        'senha': '123',
        'confirmar_senha': '123',
    })
    assert resp.status_code == 200
    assert 'mínimo 8 caracteres' in resp.get_data(as_text=True)


def test_registrar_usuario_com_sucesso_fica_pendente(client, db):
    from app.models import Usuario

    resp = client.post('/auth/registrar', data={
        'nome': 'Novo Usuário',
        'email': 'novo@escola.com',
        'senha': 'Senha@123',
        'confirmar_senha': 'Senha@123',
    }, follow_redirects=True)
    assert resp.status_code == 200

    criado = Usuario.query.filter_by(email='novo@escola.com').first()
    assert criado is not None
    assert criado.aprovado is False
