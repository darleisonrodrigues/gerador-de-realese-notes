import sqlite3
import json
from datetime import datetime
from pathlib import Path
import streamlit as st

class CollaborativeReleaseNotesDB:
    def __init__(self, db_path="collaborative_release_notes.db"):
        self.db_path = db_path
        self.init_database()
    
    def clear_database(self):
        """Limpa todos os dados do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deletar todas as tasks primeiro (devido à foreign key)
        cursor.execute("DELETE FROM tasks")
        
        # Deletar todas as versões
        cursor.execute("DELETE FROM release_versions")
        
        # Resetar os auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('tasks', 'release_versions')")
        
        conn.commit()
        conn.close()
        print("Banco de dados limpo com sucesso!")

    def init_database(self):
        """Inicializa o banco de dados colaborativo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para versões de release
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS release_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                final_markdown TEXT
            )
        ''')
        
        # Tabela para tasks individuais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id INTEGER,
                jira_task_id TEXT NOT NULL,
                task_type TEXT NOT NULL, -- 'História' ou 'Bug'
                task_title TEXT NOT NULL,
                task_description TEXT NOT NULL,
                generated_content TEXT NOT NULL,
                evidence_image TEXT,
                developer_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (version_id) REFERENCES release_versions (id),
                UNIQUE(version_id, jira_task_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_version_if_exists(self, version_name):
        """Pega uma versão específica apenas se ela existir, sem criar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar versão específica
        cursor.execute("SELECT id FROM release_versions WHERE version_name = ?", (version_name,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0], version_name
        else:
            return None, None

    def get_or_create_version(self, version_name):
        """Pega uma versão específica ou cria uma nova"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar versão específica
        cursor.execute("SELECT id FROM release_versions WHERE version_name = ?", (version_name,))
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return result[0], version_name
        
        # Criar nova versão se não existir
        cursor.execute("INSERT INTO release_versions (version_name, is_active) VALUES (?, FALSE)", (version_name,))
        version_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return version_id, version_name
    
    def get_or_create_active_version(self):
        """Pega a versão ativa ou cria uma nova (método antigo mantido para compatibilidade)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar versão ativa
        cursor.execute("SELECT id, version_name FROM release_versions WHERE is_active = TRUE LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return result[0], result[1]
        
        # Criar nova versão se não existir
        version_name = f"v{datetime.now().strftime('%Y.%m.%d')}"
        cursor.execute("INSERT INTO release_versions (version_name) VALUES (?)", (version_name,))
        version_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return version_id, version_name
    
    def add_task(self, task_data, generated_content, version_name=None):
        """Adiciona uma nova task à versão especificada"""
        if version_name:
            version_id, version_name = self.get_or_create_version(version_name)
        else:
            version_id, version_name = self.get_or_create_active_version()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (version_id, jira_task_id, task_type, task_title, task_description, 
                 generated_content, evidence_image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                version_id,
                task_data['jira_task_id'],
                task_data['tipo_task'],
                task_data['jira_task_title'],
                task_data['jira_task_description'],
                generated_content,
                task_data.get('evidence_image', '')
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            st.error(f"Erro ao adicionar task: {str(e)}")
            return False
        finally:
            conn.close()
    
    def generate_collaborative_markdown(self, version_name=None):
        """Gera o markdown colaborativo para uma versão específica"""
        if version_name:
            version_id, version_name_found = self.get_version_if_exists(version_name)
            if not version_id:
                # Se a versão não existe, retorna mensagem padrão sem criar
                return "Nenhuma task adicionada ainda para esta versão."
        else:
            version_id, _ = self.get_or_create_active_version()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar todas as tasks da versão
        cursor.execute('''
            SELECT task_type, jira_task_id, task_title, generated_content, evidence_image, developer_name
            FROM tasks 
            WHERE version_id = ?
            ORDER BY 
                CASE task_type 
                    WHEN 'User Story' THEN 1
                    WHEN 'Bug' THEN 2
                    WHEN 'Improvement' THEN 3
                    WHEN 'Technical Debt' THEN 4
                    ELSE 5
                END,
                created_at ASC
        ''', (version_id,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            return "[[_TOC_]]\n\n---\n\n*Nenhuma task adicionada ainda*"
        
        # Verificar se há conteúdo editado manualmente
        manual_edit_task = [t for t in tasks if t[0] == 'MANUAL_EDIT']
        if manual_edit_task:
            # Se há conteúdo editado manualmente, retornar diretamente
            return manual_edit_task[0][3]  # generated_content
        
        # Caso contrário, montar markdown colaborativo das tasks normais
        markdown = "[[_TOC_]]\n\n---\n\n"
        
        # Separar por tipo usando os novos tipos
        user_stories = [t for t in tasks if t[0] == 'User Story']
        bugs = [t for t in tasks if t[0] == 'Bug']
        improvements = [t for t in tasks if t[0] == 'Improvement']
        technical_debts = [t for t in tasks if t[0] == 'Technical Debt']
        
        # Adicionar seções na ordem especificada
        if user_stories:
            markdown += "##User Story\n"
            for task in user_stories:
                markdown += f"{task[3]}\n\n"
        
        if bugs:
            markdown += "##Bug\n"
            for task in bugs:
                markdown += f"{task[3]}\n\n"
        
        if improvements:
            markdown += "##Improvement\n"
            for task in improvements:
                markdown += f"{task[3]}\n\n"
        
        if technical_debts:
            markdown += "##Technical Debt\n"
            for task in technical_debts:
                markdown += f"{task[3]}\n\n"
        
        return markdown.rstrip() + "\n"
    
    def get_version_stats(self, version_name=None):
        """Retorna estatísticas de uma versão específica"""
        if version_name:
            version_id, _ = self.get_version_if_exists(version_name)
            if not version_id:
                # Se a versão não existe, retorna stats vazias
                return {
                    'total': 0,
                    'user_stories': 0,
                    'bugs': 0,
                    'improvements': 0,
                    'technical_debts': 0
                }
        else:
            version_id, _ = self.get_or_create_active_version()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT task_type, COUNT(*) 
            FROM tasks 
            WHERE version_id = ? 
            GROUP BY task_type
        ''', (version_id,))
        
        stats = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE version_id = ?', (version_id,))
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'user_stories': stats.get('User Story', 0),
            'bugs': stats.get('Bug', 0),
            'improvements': stats.get('Improvement', 0),
            'technical_debts': stats.get('Technical Debt', 0)
        }
    
    def list_all_versions(self):
        """Lista todas as versões"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id, v.version_name, v.created_at, v.is_active, COUNT(t.id) as task_count
            FROM release_versions v
            LEFT JOIN tasks t ON v.id = t.version_id
            GROUP BY v.id, v.version_name, v.created_at, v.is_active
            ORDER BY v.created_at DESC
        ''')
        
        versions = cursor.fetchall()
        conn.close()
        
        return versions
    
    def create_new_version(self, version_name):
        """Cria uma nova versão e desativa a atual"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Desativar versão atual
        cursor.execute("UPDATE release_versions SET is_active = FALSE")
        
        # Criar nova versão
        cursor.execute("INSERT INTO release_versions (version_name, is_active) VALUES (?, TRUE)", (version_name,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_all_versions(self):
        """Retorna todas as versões existentes ordenadas por data de criação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, version_name, created_at, is_active 
            FROM release_versions 
            ORDER BY created_at DESC
        """)

        versions = cursor.fetchall()
        conn.close()

        return versions
    
    def update_version_content(self, version_name, new_content):
        """Atualiza o conteúdo de uma versão específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se a versão existe
            cursor.execute("SELECT id FROM release_versions WHERE version_name = ?", (version_name,))
            version_result = cursor.fetchone()
            
            if not version_result:
                raise Exception(f"Versão {version_name} não encontrada")
            
            version_id = version_result[0]
            
            # Limpar todas as tasks da versão
            cursor.execute("DELETE FROM tasks WHERE version_id = ?", (version_id,))
            
            # Inserir o conteúdo editado como uma task especial que será reconhecida
            cursor.execute("""
                INSERT INTO tasks 
                (version_id, jira_task_id, task_type, task_title, task_description, generated_content, evidence_image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                'MANUAL_EDIT',
                'MANUAL_EDIT',  # Tipo especial para conteúdo editado manualmente
                'Conteúdo Editado Manualmente',
                'Conteúdo completo editado pelo usuário',
                new_content,
                None
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao atualizar versão: {str(e)}")
        finally:
            conn.close()
    
    def delete_version(self, version_name):
        """Exclui uma versão e todas as suas tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se a versão existe
            cursor.execute("SELECT id FROM release_versions WHERE version_name = ?", (version_name,))
            version_result = cursor.fetchone()
            
            if not version_result:
                raise Exception(f"Versão {version_name} não encontrada")
            
            version_id = version_result[0]
            
            # Excluir todas as tasks da versão
            cursor.execute("DELETE FROM tasks WHERE version_id = ?", (version_id,))
            
            # Excluir a versão
            cursor.execute("DELETE FROM release_versions WHERE id = ?", (version_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao excluir versão: {str(e)}")
        finally:
            conn.close()

def get_collaborative_db():
    """Função helper para usar no Streamlit"""
    return CollaborativeReleaseNotesDB()