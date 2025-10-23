import requests
import json
import os
from database.collaborative_db import get_collaborative_db

class ReleaseNotesCrewAI:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.db = get_collaborative_db()
    
    def generate_simple_description(self, task_data):
        """Gera descrição simples usando API do Groq via requests"""
        try:
            prompt = f"""Você é um especialista em documentação técnica. Crie uma descrição concisa e clara para release notes.

ENTRADA:
Task ID: {task_data['jira_task_id']}
Tipo: {task_data['tipo_task']} 
Descrição: {task_data['jira_task_description']}

INSTRUÇÕES:
1. Não use tags <think> ou qualquer marcação de raciocínio
2. Para História: Explique o que foi implementado, como funciona e qual o benefício
3. Para Bug: Explique qual era o problema e como foi resolvido
4. Use linguagem clara e profissional (2-5 frases)
5. Retorne APENAS o texto descritivo, sem título ou formatação

EXEMPLO História:
"Adicionamos um informativo mostrando o motivo do status de 'bloqueado' e status 'em observação'. Essa bottomsheet é mostrada ao clicar no status dos pontos de venda, na tela de Minuto de ouro e nas listagens de Rotas e Carteira."

EXEMPLO Bug:
"Existia um bug no app em que o PDF de um pedido tinha o 'valor unitário' e 'preço por KG' calculados incorretamente. Esse valor estava errado apenas no PDF, na tela de consulta estava correto. Nessa versão igualamos as duas informações, calculando corretamente para itens com peso variável."

Gere apenas a descrição:"""
            
            result = self._call_groq_api(prompt)
            return self._clean_response(result)
                
        except Exception as e:
            raise Exception(f"Erro ao gerar descrição: {str(e)}")
    
    def _clean_response(self, text):
        """Remove tags de raciocínio e limpa a resposta"""
        import re
        # Remove tags <think>...</think>
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Remove linhas vazias extras
        text = re.sub(r'\n\s*\n', '\n', text)
        # Remove espaços no início e fim
        return text.strip()
    
    def generate_release_notes(self, task_data, image_path=None, version_name=None):
        """Gera release notes e adiciona ao sistema colaborativo"""
        try:
            # Preparar informação da imagem
            image_info = ""
            if image_path and task_data.get('evidence_image'):
                image_info = f"\n![{task_data['evidence_image']}](/.attachments/{task_data['evidence_image']} =300x)"
            
            prompt = f"""Você é um redator técnico especialista. Crie uma release note seguindo EXATAMENTE o formato especificado.

ENTRADA:
- Task ID: {task_data['jira_task_id']}
- Tipo: {task_data['tipo_task']} 
- Título: {task_data['jira_task_title']}
- Descrição: {task_data['jira_task_description']}

FORMATO OBRIGATÓRIO:
###[{task_data['jira_task_id']}] {task_data['jira_task_title']}

[Descrição clara em 2-4 frases explicando a funcionalidade/correção]{image_info}

---

REGRAS:
1. NÃO inclua raciocínio, pensamentos ou tags <think>
2. Para História: Explique o que foi implementado e o benefício para o usuário
3. Para Bug: Explique qual era o problema e como foi resolvido
4. Use linguagem clara e profissional
5. Mantenha entre 2-4 frases
6. SEMPRE termine com "---"
7. NÃO adicione cabeçalhos como ##História ou ##Bug
8. Retorne APENAS o bloco da release note

EXEMPLO DE SAÍDA ESPERADA:
###[JBSV-3263] Crédito/Cliente Bloqueado – Consultar o status e já retornar o direcional

Adicionamos um informativo mostrando o motivo do status de "bloqueado" e status "em observação". Essa bottomsheet é mostrada ao clicar no status dos pontos de venda, na tela de Minuto de ouro e nas listagens de Rotas e Carteira.

![motivo-de-bloqueio.png](/.attachments/motivo-de-bloqueio.png =300x)

---

Gere agora a release note seguindo exatamente este formato:"""

            # Gerar o conteúdo
            generated_content = self._call_groq_api(prompt)
            
            # Adicionar ao banco colaborativo com versão específica
            self.db.add_task(task_data, generated_content, version_name)
            
            # Retornar o markdown colaborativo da versão específica
            return self.db.generate_collaborative_markdown(version_name)
            
        except Exception as e:
            raise Exception(f"Erro ao gerar release notes: {str(e)}")
    
    def get_collaborative_release_notes(self, version_name=None):
        """Retorna as release notes colaborativas de uma versão específica"""
        return self.db.generate_collaborative_markdown(version_name)
    
    def get_version_stats(self, version_name=None):
        """Retorna estatísticas de uma versão específica"""
        return self.db.get_version_stats(version_name)
    
    def get_version_stats_by_name(self, version_name):
        """Retorna estatísticas de uma versão específica pelo nome"""
        return self.db.get_version_stats(version_name)
    
    def _call_groq_api(self, prompt):
        """Chama a API do Groq usando requests diretamente"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configuração específica para openai/gpt-oss-20b
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": float(os.getenv("TEMPERATURE", 0.6)),
            "max_completion_tokens": 8192,
            "top_p": 1,
            "reasoning_effort": "medium"
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._clean_response(content).strip()
        else:
            raise Exception(f"Erro na API: {response.status_code} - {response.text}")

# Função auxiliar para usar no Streamlit
def create_release_notes_crew():
    return ReleaseNotesCrewAI()