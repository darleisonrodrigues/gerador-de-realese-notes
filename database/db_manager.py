import sqlite3
import json
from datetime import datetime
from pathlib import Path
import streamlit as st

class ReleaseNotesDB:
    def __init__(self, db_path="release_notes.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para armazenar entries de release notes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS release_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jira_task_id TEXT NOT NULL,
                task_title TEXT NOT NULL,
                task_type TEXT NOT NULL,
                task_description TEXT NOT NULL,
                generated_content TEXT,
                evidence_image_name TEXT,
                evidence_image_data BLOB,
                developer_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sprint_version TEXT,
                status TEXT DEFAULT 'draft'
            )
        ''')
        
        # Tabela para gerenciar sprints/versões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sprint_name TEXT UNIQUE NOT NULL,
                version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                description TEXT
            )
        ''')
        
        # Tabela para documentos RAG (PDFs de exemplo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_release_entry(self, entry_data):
        """Salva uma entry de release note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO release_entries 
                (jira_task_id, task_title, task_type, task_description, 
                 generated_content, evidence_image_name, evidence_image_data, 
                 developer_name, sprint_version, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_data['jira_task_id'],
                entry_data['task_title'],
                entry_data['task_type'],
                entry_data['task_description'],
                entry_data.get('generated_content', ''),
                entry_data.get('evidence_image_name'),
                entry_data.get('evidence_image_data'),
                entry_data.get('developer_name', ''),
                entry_data.get('sprint_version', 'current'),
                entry_data.get('status', 'draft')
            ))
            
            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id
            
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar entry: {e}")
            return None
        finally:
            conn.close()
    
    def update_release_entry(self, entry_id, entry_data):
        """Atualiza uma entry existente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE release_entries 
                SET task_title=?, task_type=?, task_description=?, 
                    generated_content=?, evidence_image_name=?, evidence_image_data=?,
                    developer_name=?, sprint_version=?, status=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                entry_data['task_title'],
                entry_data['task_type'],
                entry_data['task_description'],
                entry_data.get('generated_content', ''),
                entry_data.get('evidence_image_name'),
                entry_data.get('evidence_image_data'),
                entry_data.get('developer_name', ''),
                entry_data.get('sprint_version', 'current'),
                entry_data.get('status', 'draft'),
                entry_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            st.error(f"Erro ao atualizar entry: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_entries(self, sprint_version=None):
        """Recupera todas as entries, opcionalmente filtradas por sprint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if sprint_version:
                cursor.execute('''
                    SELECT * FROM release_entries 
                    WHERE sprint_version = ? 
                    ORDER BY created_at DESC
                ''', (sprint_version,))
            else:
                cursor.execute('''
                    SELECT * FROM release_entries 
                    ORDER BY created_at DESC
                ''')
            
            entries = []
            for row in cursor.fetchall():
                entry = {
                    'id': row[0],
                    'jira_task_id': row[1],
                    'task_title': row[2],
                    'task_type': row[3],
                    'task_description': row[4],
                    'generated_content': row[5],
                    'evidence_image_name': row[6],
                    'evidence_image_data': row[7],
                    'developer_name': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'sprint_version': row[11],
                    'status': row[12]
                }
                entries.append(entry)
            
            return entries
            
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar entries: {e}")
            return []
        finally:
            conn.close()
    
    def get_entry_by_id(self, entry_id):
        """Recupera uma entry específica por ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM release_entries WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'jira_task_id': row[1],
                    'task_title': row[2],
                    'task_type': row[3],
                    'task_description': row[4],
                    'generated_content': row[5],
                    'evidence_image_name': row[6],
                    'evidence_image_data': row[7],
                    'developer_name': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'sprint_version': row[11],
                    'status': row[12]
                }
            return None
            
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar entry: {e}")
            return None
        finally:
            conn.close()
    
    def delete_entry(self, entry_id):
        """Deleta uma entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM release_entries WHERE id = ?', (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            st.error(f"Erro ao deletar entry: {e}")
            return False
        finally:
            conn.close()
    
    def create_sprint(self, sprint_name, version, description=""):
        """Cria uma nova sprint/versão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sprints (sprint_name, version, description)
                VALUES (?, ?, ?)
            ''', (sprint_name, version, description))
            
            sprint_id = cursor.lastrowid
            conn.commit()
            return sprint_id
            
        except sqlite3.IntegrityError:
            st.error(f"Sprint '{sprint_name}' já existe!")
            return None
        except sqlite3.Error as e:
            st.error(f"Erro ao criar sprint: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_sprints(self):
        """Recupera todas as sprints"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM sprints ORDER BY created_at DESC')
            sprints = []
            for row in cursor.fetchall():
                sprint = {
                    'id': row[0],
                    'sprint_name': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'status': row[4],
                    'description': row[5]
                }
                sprints.append(sprint)
            return sprints
            
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar sprints: {e}")
            return []
        finally:
            conn.close()
    
    def get_entries_by_type(self, task_type, sprint_version=None):
        """Recupera entries por tipo (História ou Bug)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if sprint_version:
                cursor.execute('''
                    SELECT * FROM release_entries 
                    WHERE task_type = ? AND sprint_version = ?
                    ORDER BY created_at DESC
                ''', (task_type, sprint_version))
            else:
                cursor.execute('''
                    SELECT * FROM release_entries 
                    WHERE task_type = ?
                    ORDER BY created_at DESC
                ''', (task_type,))
            
            entries = []
            for row in cursor.fetchall():
                entry = {
                    'id': row[0],
                    'jira_task_id': row[1],
                    'task_title': row[2],
                    'task_type': row[3],
                    'task_description': row[4],
                    'generated_content': row[5],
                    'evidence_image_name': row[6],
                    'evidence_image_data': row[7],
                    'developer_name': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'sprint_version': row[11],
                    'status': row[12]
                }
                entries.append(entry)
            
            return entries
            
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar entries por tipo: {e}")
            return []
        finally:
            conn.close()
    
    def generate_final_markdown(self, sprint_version=None):
        """Gera o markdown final compilado para download"""
        historias = self.get_entries_by_type("História", sprint_version)
        bugs = self.get_entries_by_type("Bug", sprint_version)
        
        markdown_content = "[[TOC]]\n\n"
        
        # Seção Histórias
        if historias:
            markdown_content += "## História\n"
            for historia in historias:
                if historia['generated_content']:
                    markdown_content += historia['generated_content'] + "\n\n"
        
        # Seção Bugs
        if bugs:
            markdown_content += "## Bug\n"
            for bug in bugs:
                if bug['generated_content']:
                    markdown_content += bug['generated_content'] + "\n\n"
        
        return markdown_content
    
    def save_rag_document(self, filename, content, file_size):
        """Salva documento para RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO rag_documents (filename, content, file_size, processed)
                VALUES (?, ?, ?, ?)
            ''', (filename, content, file_size, True))
            
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
            
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar documento RAG: {e}")
            return None
        finally:
            conn.close()
    
    def get_rag_documents(self):
        """Recupera todos os documentos RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM rag_documents ORDER BY upload_date DESC')
            documents = []
            for row in cursor.fetchall():
                doc = {
                    'id': row[0],
                    'filename': row[1],
                    'content': row[2],
                    'upload_date': row[3],
                    'file_size': row[4],
                    'processed': row[5]
                }
                documents.append(doc)
            return documents
            
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar documentos RAG: {e}")
            return []
        finally:
            conn.close()