# Claviculario_v3

## 📝 Visão Geral

`Claviculario_v3` é uma aplicação web em Python/Flask para controle de empréstimo de chaves em escolas ou instituições. Ela oferece:

- cadastro e aprovação de usuários (Admin/Comum)
- empréstimo e devolução de chaves
- histórico de movimentações
- controle de sessões ativas e expiração
- exportação de relatórios em PDF
- painel de administração para gestão de usuários e chaves

## 🚀 Recursos Principais

1. Autenticação segura (login/registro) com validação de e-mail e senha.
2. Gerenciamento de usuários:
   - Admin aprova/rejeita cadastros
   - Admin bane e desbana usuários
   - Admin cria usuários manualmente
3. Gerenciamento de chaves:
   - cadastrar, excluir, retirar e devolver
   - status: Disponível, Em Uso, Pendente
4. Histórico de movimentações com filtro por período.
5. Relatório em PDF do histórico de empréstimos.
6. Verificação de sessão por token (limite máximo por usuário e expiração automática).

## 📁 Estrutura do Projeto

- `run.py` - inicializa a aplicação
- `config.py` - configurações gerais (secret key, banco de dados)
- `requirements.txt` - dependências Python
- `app/`
  - `__init__.py` - factory app, blueprints, sessão global
  - `extensions.py` - instâncias `db`, `login_manager`, `csrf`
  - `models.py` - definição de modelos: `Usuario`, `Chave`, `Movimentacao`, `SessaoAtiva`
  - `auth/` - rotas de autenticação
  - `admin/` - rotas de administração
  - `chaves/` - rotas de controle de chaves
  - `utils/pdf.py` - geração de relatório PDF
- `templates/` - HTML das páginas (login, cadastro, painel, etc.)
- `logs/` - logs da aplicação (se configurado)

## ⚙️ Instalação Rápida

1. Clone o repositório:

```bash
git clone <url-do-repositório>
cd claviculario_v3
```

2. Crie e ative um ambiente virtual:

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale dependências (use `requirements-dev.txt` se for rodar testes/lint):

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# ou, para desenvolvimento:
python -m pip install -r requirements-dev.txt
```

## 🛠️ Configuração Básica

Toda a configuração vem de variáveis de ambiente (nunca de valores fixos no código). Copie o arquivo de exemplo e ajuste:

```bash
cp .env.example .env
```

Principais variáveis (veja `.env.example` para a lista completa):

- `SECRET_KEY` — obrigatória fora do modo debug. Gere uma com:
  `python -c "import secrets; print(secrets.token_hex(32))"`
- `FLASK_DEBUG` — `1` para desenvolvimento local (nunca em produção).
- `DATABASE_URL` — string de conexão (padrão: SQLite local).
- `MAX_SESSOES_POR_USUARIO` — limite de sessões simultâneas por usuário.
- `SESSION_COOKIE_SECURE` — defina `1` quando a aplicação rodar atrás de HTTPS.

Sem `SECRET_KEY` definida e sem `FLASK_DEBUG=1`, a aplicação falha ao subir com um erro claro, em vez de usar uma chave padrão insegura.

## ▶️ Como Executar

1. Inicie a base de dados e dados iniciais (rodar uma única vez):

```bash
FLASK_DEBUG=1 python run.py
```

Acesse no navegador:

`http://127.0.0.1:5000/setup`

2. Abra o sistema:

`http://127.0.0.1:5000/`

## 🔐 Credenciais Iniciais

Após `/setup`, ficam disponíveis:

- Admin: `admin@escola.com` / `Admin@123`
- Usuário Comum: `joao@escola.com` / `Joao@123`

## 🧭 Rotas Principais

- `/` → redireciona para painel
- `/auth/login` → login
- `/auth/registrar` → cadastro de usuário
- `/auth/aguardando-aprovacao` → tela de espera até aprovação
- `/auth/minhas-sessoes` → lista sessões ativas do usuário
- `/chaves/painel` → painel de chaves e histórico
- `/admin/usuarios` → gerenciamento Admin de usuários
- `/setup` → inicializa banco e dados de exemplo

## 🧪 Testes e Lint

Suíte automatizada com pytest e lint com ruff (ambos rodam no CI a cada push/PR):

```bash
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
```

Roteiro manual complementar:

- Login como Admin e Comum
- Aprovar/Rejeitar/banir usuários
- Cadastrar/Excluir chaves
- Retirar/Devolver/Confirmar devolução
- Filtrar histórico e exportar PDF
- Checar expiração de sessão ao ficar inativo

## ❗ Dicas de Operação

- Use senha forte e variáveis de ambiente em produção (veja `.env.example`).
- Não deixe `SECRET_KEY` pública nem versionada no `.env`.
- Use banco PostgreSQL/MySQL se for ambiente que não seja local.
- Se usar SQLite, garanta permissão de escrita em `app.db`.
- Nunca rode com `FLASK_DEBUG=1` em produção (expõe o debugger interativo do Werkzeug, que permite execução remota de código).
- Não use o servidor de desenvolvimento do Flask (`python run.py`) em produção; sirva a aplicação com um WSGI server, ex.: `gunicorn -w 4 run:app`.

## 🛑 Problemas Comuns

- `sqlalchemy.exc.OperationalError`: string de conexão errada
- `TemplateNotFound`: caminho errado no `template_folder` ou arquivos ausentes
- `RuntimeError (working outside of request context)`: execute rotas via navegador/postman, não por shell

## 📄 Licença e Contato

- Projeto educativo/sem licença definida (insira `LICENSE` se quiser)
- Mantido por: Alexandre Sampaio Rodrigues

---
