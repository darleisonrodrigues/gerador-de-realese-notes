from groq import Groq
import os

class ReleaseNotesCrewAI:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    def generate_simple_description(self, task_data):
        """Gera descrição simples usando prompt específico"""
        try:
            prompt = f"""# Você é um especialista em documentação técnica. Sua tarefa é criar uma descrição concisa e clara para release notes com base na descrição de uma task do Jira.

## ENTRADA
Task ID: {task_data['jira_task_id']}
Tipo: {task_data['tipo_task']} 
Descrição original: 
{task_data['jira_task_description']}

## SAÍDA ESPERADA
Gere APENAS o texto descritivo que irá abaixo do título da task. Não inclua o título da task, links ou formatação de imagens. Seu texto deve:

1. Para História: Explicar o que foi implementado, como funciona do ponto de vista do usuário e qual o benefício.
2. Para Bug: Explicar qual era o problema e como foi resolvido.

Use linguagem clara e profissional, evite termos técnicos desnecessários, e mantenha o texto entre 2-5 frases.

Exemplo do formato esperado para História:
"Adicionamos um informativo mostrando o motivo do status de 'bloqueado' e status 'em observação'. Essa bottomsheet é mostrada ao clicar no status dos pontos de venda, na tela de Minuto de ouro e nas listagens de Rotas e Carteira."

Exemplo do formato esperado para Bug:
"Existia um bug no app em que o PDF de um pedido tinha o 'valor unitário' e 'preço por KG' calculados incorretamente. Esse valor estava errado apenas no PDF, na tela de consulta estava correto. Nessa versão igualamos as duas informações, calculando corretamente para itens com peso variável."
"""
            
            # Usar a API do Groq diretamente
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            raise Exception(f"Erro ao gerar descrição: {str(e)}")
    
    def generate_release_notes(self, task_data, image_path=None):
        """Gera release notes usando API do Groq diretamente"""
        try:
            # Preparar informação da imagem
            image_info = ""
            if image_path and task_data.get('evidence_image'):
                image_info = f"\n![{task_data['evidence_image']}](/.attachments/{task_data['evidence_image']} =300x)"
            
            prompt = f"""# Você é um especialista em documentação técnica. Crie uma release note profissional formatada em markdown.

## ENTRADA
Task ID: {task_data['jira_task_id']}
Tipo: {task_data['tipo_task']} 
Título: {task_data['jira_task_title']}
Descrição: {task_data['jira_task_description']}

## FORMATO EXATO DA SAÍDA
Gere EXATAMENTE neste formato markdown:

###[{task_data['jira_task_id']}] {task_data['jira_task_title']}

[Aqui você escreve 2-4 frases explicando a funcionalidade/correção de forma clara e profissional]{image_info}

---

## REGRAS IMPORTANTES:
1. Para História: Explique o que foi implementado e qual o benefício para o usuário
2. Para Bug: Explique qual era o problema e como foi resolvido
3. Use linguagem clara e profissional
4. Mantenha entre 2-4 frases
5. Não adicione links além da imagem (se fornecida)
6. SEMPRE termine com "---"

Retorne APENAS o markdown formatado."""

            # Chamar a API do Groq
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Erro ao gerar release notes: {str(e)}")

# Função auxiliar para usar no Streamlit
def create_release_notes_crew():
    return ReleaseNotesCrewAI()