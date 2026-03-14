# Claviculario_v3

Aplicação Flask para controle de empréstimo de chaves em ambiente escolar, com gerenciamento de usuários Admin/Comum, logs de sessões, relatórios em PDF e segurança CSRF.

## Requisitos

- Python 3.9 ou superior (testado em Python 3.13)
- Git (opcional)
- pacotes Python listados em `requirements.txt`

## Pré-configuração

1. Clonar o repositório:

   ```bash
   git clone <url-do-repositório>
   cd claviculario_v3
   ```

2. Criar ambiente virtual (recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. Atualize `requirements.txt` se desejar lock de versões específico.

4. Instalar dependências:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

## Configuração de ambiente

A aplicação usa `config.Config` em `config.py`. Exemplo de campos:

- `SECRET_KEY` - chave secreta do Flask (mantenha segura).
- `SQLALCHEMY_DATABASE_URI` - string de conexão do banco (padrão SQLite `sqlite:///app.db`).
- `SQLALCHEMY_TRACK_MODIFICATIONS=False`.

Exemplo (padrão em `config.py`):

```python
class Config:
    SECRET_KEY = 'mudar_esta_chave'  # preferível usar variáveis de ambiente
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Para usar variáveis de ambiente (Windows PowerShell):

```powershell
$env:FLASK_APP='run.py'
$env:SECRET_KEY='uma_chave_segura_aqui'
$env:DATABASE_URL='sqlite:///app.db'
```

## Inicialização

1. Criar tabelas e dados iniciais (apenas uma vez):
   - Inicie o servidor e acesse `http://127.0.0.1:5000/setup`
   - O endpoint adiciona um usuário Admin e um usuário Comum, e algumas chaves iniciais.

2. Start do servidor:

   ```bash
   python run.py
   ```

3. Acessar no navegador:
   - `http://127.0.0.1:5000/`

4. Rotas principais:
   - `/auth/login` - login
   - `/auth/registrar` - registro
   - `/admin` - painel de administração (Admin)
   - `/chaves` - lista e controle de chaves

## Usuários padrão gerados no setup

- Admin: `admin@escola.com` / `Admin@123`
- Comum: `joao@escola.com` / `Joao@123`

## Banco de dados

Padrão usa SQLite (`app.db`) na raiz. Para mudar:

1. Atualize `config.py` ou use `SQLALCHEMY_DATABASE_URI` com MySQL/PostgreSQL.
2. Exemplo PostgreSQL:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:senha@localhost:5432/nome_do_banco'
```

3. Execute `python run.py` e acesse `/setup` para criar esquema e registros iniciais.

## Estrutura de pastas

- `app/`
  - `__init__.py` - fábrica do Flask, blueprints, verificação de sessão
  - `extensions.py` - instancia SQLAlchemy, LoginManager, CSRF
  - `models.py` - definição de modelos `Usuario`, `Chave`, `SessaoAtiva`
  - `auth/`, `admin/`, `chaves/` - blueprints e rotas
  - `utils/pdf.py` - geração de PDF
- `templates/` - layouts e telas (login, cadastro, chaves, admin)
- `run.py` - inicia a aplicação
- `config.py` - classe de configuração

## Testes manuais

- Faça login com Admin, crie, edite e exclua usuários/chaves
- Simule timeout de sessão em `SessaoAtiva` e verifique logout automático
- Geração de PDF (função em `app/utils/pdf.py`)

## Problemas comuns

- `sqlalchemy.exc.OperationalError` → verifique `SQLALCHEMY_DATABASE_URI`
- `Working outside of application context` → certifique-se de usar `current_app` dentro da app
- Erro ao criar ambiente virtual → use Python 3.9+ e reinstale dependências

## Parar o servidor

- No terminal em foreground: `Ctrl+C`
- Se rodando em background no VS Code: clique em parar ou fechar terminal.

---

Mantido por: [Alexandre Sampaio Rodrigues]
