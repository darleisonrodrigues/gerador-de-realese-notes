from crewai import Agent, Task, Crew
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
    
    def create_agents(self):
        """Cria os agentes especializados para gerar release notes"""
        
        # Agente 1: Analista de Requirements
        requirements_analyst = Agent(
            role="Analista de Requirements",
            goal="Analisar e interpretar as descrições de tasks do Jira para identificar funcionalidades e impactos",
            backstory="""Você é um analista experiente em desenvolvimento de software que trabalha há anos 
            analisando requirements e documentações técnicas. Você tem a habilidade de extrair informações 
            importantes de descrições técnicas e transformá-las em insights claros sobre o que foi implementado.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agente 2: Redator Técnico
        technical_writer = Agent(
            role="Redator Técnico Especialista em Release Notes",
            goal="Criar descrições claras e amigáveis para usuários finais sobre novas funcionalidades e correções",
            backstory="""Você é um redator técnico especializado em comunicação para usuários finais. 
            Sua expertise está em transformar informações técnicas complexas em linguagem clara e acessível, 
            focando sempre nos benefícios e impactos práticos para o usuário. Você entende perfeitamente 
            o formato e estilo de release notes corporativas.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agente 3: Revisor de Release Notes
        release_notes_reviewer = Agent(
            role="Revisor e Formatador de Release Notes",
            goal="Garantir que as release notes sigam o formato correto e padrões estabelecidos",
            backstory="""Você é um especialista em documentação técnica e conhece profundamente 
            os padrões de release notes para o Azure DevOps. Você garante que toda documentação 
            siga os formatos corretos, tenha consistência de estilo e atenda aos padrões corporativos.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        return requirements_analyst, technical_writer, release_notes_reviewer
    
    def create_tasks(self, task_data, agents, image_path=None):
        """Cria as tasks para cada agente"""
        requirements_analyst, technical_writer, release_notes_reviewer = agents
        
        # Task 1: Análise de Requirements
        analysis_task = Task(
            description=f"""
            Analise a seguinte task do Jira e extraia informações importantes:
            
            **Tipo:** {task_data['tipo_task']}
            **ID:** {task_data['jira_task_id']}
            **Título:** {task_data['jira_task_title']}
            **Descrição:** {task_data['jira_task_description']}
            {f"**Imagem de evidência:** {task_data['evidence_image']}" if task_data['evidence_image'] else ""}
            
            Identifique:
            1. O que foi implementado ou corrigido
            2. Qual o impacto para o usuário final
            3. Principais benefícios e funcionalidades
            4. Contexto de uso
            
            Forneça uma análise estruturada que será usada para criar a release note.
            """,
            agent=requirements_analyst,
            expected_output="Análise estruturada da task identificando funcionalidades, impactos e benefícios para o usuário"
        )
        
        # Task 2: Redação da Release Note
        writing_task = Task(
            description=f"""
            Com base na análise fornecida, escreva uma release note no estilo corporativo seguindo este exemplo:
            
            EXEMPLO DE FORMATO:
            ```
            ###[JBSV-3061] Módulo Supervisor
            
            O Módulo do Supervisor chegou para facilitar a gestão do time e dar mais clareza sobre os resultados, tudo em um só lugar dentro do Venda+.
            
            Agora, ao acessar o aplicativo com seu login, o supervisor pode selecionar o seu próprio CPF no momento do login e visualizar um painel de gerenciamento completo do time, com indicadores consolidados e também a possibilidade de detalhar vendedor por vendedor.
            
            📊 **Principais funcionalidades:**
            
            • Funcionalidade 1 explicada de forma clara
            • Funcionalidade 2 com benefícios práticos
            • Funcionalidade 3 focada no usuário
            
            ✅ **Benefícios:**
            
            • Benefício prático 1
            • Benefício prático 2
            • Benefício prático 3
            ```
            
            IMPORTANTE:
            - Use linguagem clara e focada no usuário final
            - Destaque os benefícios práticos
            - Use emojis para tornar mais atrativo
            - Mantenha o tom profissional mas amigável
            - Organize as informações de forma hierárquica
            - Para BUGS, foque na correção e melhoria da experiência
            
            Tipo da task: {task_data['tipo_task']}
            """,
            agent=technical_writer,
            expected_output="Release note bem escrita, clara e focada no usuário final",
            context=[analysis_task]
        )
        
        # Task 3: Revisão e Formatação Final
        review_task = Task(
            description=f"""
            Revise e formate a release note para garantir que siga EXATAMENTE este formato:
            
            Para HISTÓRIA:
            ```
            ###[{task_data['jira_task_id']}] {task_data['jira_task_title']}
            
            [Conteúdo da release note formatado]
            
            {f"![{task_data['evidence_image']}](/.attachments/{task_data['evidence_image']} =300x)" if task_data['evidence_image'] else ""}
            
            ---
            ```
            
            Para BUG:
            ```
            ###[{task_data['jira_task_id']}] {task_data['jira_task_title']}
            
            [Conteúdo da release note formatado explicando a correção]
            
            {f"![{task_data['evidence_image']}](/.attachments/{task_data['evidence_image']} =300x)" if task_data['evidence_image'] else ""}
            
            ---
            ```
            
            VERIFICAÇÕES OBRIGATÓRIAS:
            1. Header deve ser ###[ID] Título exatamente
            2. Link da imagem deve ter o formato correto se fornecida
            3. Deve terminar com --- (linha separadora)
            4. Conteúdo deve ser claro e bem estruturado
            5. Usar markdown apropriado para formatação
            
            Retorne APENAS o markdown final formatado corretamente.
            """,
            agent=release_notes_reviewer,
            expected_output="Release note final formatada corretamente em markdown, pronta para o Azure DevOps",
            context=[writing_task]
        )
        
        return [analysis_task, writing_task, review_task]
    
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