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

3. Instale dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 🛠️ Configuração Básica

Edite `config.py` conforme seu ambiente:

```python
class Config:
    SECRET_KEY = 'mudar_esta_chave'  # use variável de ambiente em produção
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_SESSOES_POR_USUARIO = 10
```

Ou configure via variáveis de ambiente:

```powershell
setx FLASK_APP run.py
setx SECRET_KEY 'secreta'
setx DATABASE_URL 'sqlite:///app.db'
```

## ▶️ Como Executar

1. Inicie a base de dados e dados iniciais (rodar uma única vez):

```bash
python run.py
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

## 🧪 Testes e Verificações

- Login como Admin e Comum
- Aprovar/Rejeitar/banir usuários
- Cadastrar/Excluir chaves
- Retirar/Devolver/Confirmar devolução
- Filtrar histórico e exportar PDF
- Checar expiração de sessão ao ficar inativo

## ❗ Dicas de Operação

- Use senha forte e variáveis de ambiente em produção.
- Não deixe `SECRET_KEY` pública.
- Use banco PostgreSQL/MySQL se for ambiente que não seja local.
- Se usar SQLite, garanta permissão de escrita em `app.db`.

## 🛑 Problemas Comuns

- `sqlalchemy.exc.OperationalError`: string de conexão errada
- `TemplateNotFound`: caminho errado no `template_folder` ou arquivos ausentes
- `RuntimeError (working outside of request context)`: execute rotas via navegador/postman, não por shell

## 📄 Licença e Contato

- Projeto educativo/sem licença definida (insira `LICENSE` se quiser)
- Mantido por: Alexandre Sampaio Rodrigues

---
