#!/usr/bin/env python3
"""
Script de migração para quem já tem um banco.db do sistema MVP.
Lê o banco antigo (banco.db) e escreve os dados no novo banco (banco_v3.db).
Execute: python migrate.py
"""
import sqlite3
import os

OLD_DB = 'instance/banco.db'
NEW_DB = 'instance/banco_v3.db'


def migrate():
    if not os.path.exists(OLD_DB):
        print(f"[!] Banco antigo não encontrado em {OLD_DB}. Nada a migrar.")
        return

    from run import app
    from app.models import Usuario, Chave, Movimentacao, db
    from werkzeug.security import generate_password_hash

    with app.app_context():
        db.create_all()

        old = sqlite3.connect(OLD_DB)
        old.row_factory = sqlite3.Row

        # Migrar usuários
        usuarios_migrados = 0
        for row in old.execute("SELECT * FROM usuario"):
            if not Usuario.query.filter_by(email=row['email']).first():
                u = Usuario(
                    id=row['id'],
                    nome=row['nome'],
                    email=row['email'],
                    # Gerar hash seguro com senha padrão (usuário deve redefinir)
                    senha_hash=generate_password_hash(row['senha'] if 'senha' in row.keys() else 'Temp@1234'),
                    tipo=row['tipo'] or 'Comum',
                    is_active=True  # usuários existentes são aprovados
                )
                db.session.add(u)
                usuarios_migrados += 1

        # Migrar chaves
        chaves_migradas = 0
        for row in old.execute("SELECT * FROM chave"):
            if not Chave.query.filter_by(id=row['id']).first():
                c = Chave(id=row['id'], nome=row['nome'], status=row['status'])
                db.session.add(c)
                chaves_migradas += 1

        # Migrar movimentações
        movs_migradas = 0
        for row in old.execute("SELECT * FROM movimentacao"):
            if not Movimentacao.query.filter_by(id=row['id']).first():
                m = Movimentacao(
                    id=row['id'],
                    chave_id=row['chave_id'],
                    usuario_nome=row['usuario_nome'],
                    data_retirada=row['data_retirada'],
                    data_devolucao=row['data_devolucao'],
                )
                db.session.add(m)
                movs_migradas += 1

        db.session.commit()
        old.close()

        print(f"[✅] Migração concluída!")
        print(f"     Usuários: {usuarios_migrados}")
        print(f"     Chaves:   {chaves_migradas}")
        print(f"     Movim.:   {movs_migradas}")
        print()
        print("[!] IMPORTANTE: Todos os usuários migrados receberam senha provisória.")
        print("    Peça a cada um que redefina sua senha após o primeiro acesso.")


if __name__ == '__main__':
    migrate()
