import streamlit as st
import os
from PIL import Image
from agents.crew import ReleaseNotesCrewAI
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Gerador de Release Notes",
    page_icon="📝",
    layout="centered"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .task-form {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #0052a3;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown('<h1 class="main-header">📝 Gerador de Release Notes</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Transforme descrições técnicas em release notes profissionais</p>', unsafe_allow_html=True)
    
    # Configuração da API
    st.subheader("🔑 Configuração")
    groq_api_key = st.text_input(
        "Groq API Key:",
        type="password",
        help="Sua chave da API do Groq"
    )
    
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
        st.success("✅ API configurada!")
    
    st.divider()

    # Formulário principal
    st.markdown('<div class="task-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Tipo da task
        tipo_task = st.selectbox(
            "Tipo da Task:",
            options=["História", "Bug"],
            help="História = nova funcionalidade | Bug = correção"
        )
    
    with col2:
        # ID da task
        jira_task_id = st.text_input(
            "ID da Task:",
            placeholder="Ex: JBSV-3048",
            help="Formato: JBSV-XXXX"
        )
    
    # Título da task
    jira_task_title = st.text_input(
        "Título da Task:",
        placeholder="Ex: Substituir todo azul escuro do app por azul marinho",
        help="Título descritivo da funcionalidade ou correção"
    )
    
    # Descrição da task
    jira_task_description = st.text_area(
        "Descrição Completa da Task:",
        height=150,
        placeholder="Cole aqui toda a descrição da task do Jira...",
        help="Quanto mais detalhada, melhor será o resultado"
    )
    
    # Upload de imagem
    evidence_image = st.file_uploader(
        "Imagem de Evidência (opcional):",
        type=['png', 'jpg', 'jpeg'],
        help="Imagem que demonstra a implementação"
    )
    
    if evidence_image:
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(evidence_image, caption="Preview da imagem", width=300)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão de geração
    generate_button = st.button(
        "🤖 Gerar Release Note",
        disabled=not (jira_task_id and jira_task_title and jira_task_description and groq_api_key),
        help="Gera automaticamente a release note usando IA"
    )
    
    # Resultado
    if generate_button:
        if not groq_api_key:
            st.error("❌ Configure sua Groq API Key")
        else:
            try:
                with st.spinner("🤖 Gerando release note..."):
                    # Preparar dados da task
                    task_data = {
                        "tipo_task": tipo_task,
                        "jira_task_id": jira_task_id,
                        "jira_task_title": jira_task_title,
                        "jira_task_description": jira_task_description,
                        "evidence_image": evidence_image.name if evidence_image else None
                    }
                    
                    # Gerar com IA simplificada
                    crew = ReleaseNotesCrewAI()
                    description = crew.generate_simple_description(task_data)
                    
                    # Construir resultado final
                    result = f"###[{jira_task_id}] {jira_task_title}\n\n{description}"
                    
                    if evidence_image:
                        result += f"\n\n![{evidence_image.name}](/.attachments/{evidence_image.name} =300x)"
                    
                    # Exibir resultado
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### 📝 Release Note Gerada:")
                    st.code(result, language="markdown")
                    
                    # Botão de cópia
                    st.download_button(
                        label="📋 Baixar Release Note",
                        data=result,
                        file_name=f"release_note_{jira_task_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown"
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.success("✅ Release note gerada com sucesso!")
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar release note: {str(e)}")
                st.info("💡 Verifique se sua API Key está correta")
    else:
        # Mostrar exemplo quando não há geração
        st.markdown("### 📋 Exemplo de saída:")
        exemplo = f"""###[{jira_task_id or "JBSV-3048"}] {jira_task_title or "Substituir todo azul escuro do app por azul marinho"}

{f"Funcionalidade implementada com base na descrição fornecida..." if tipo_task == "História" else "Correção implementada com base na descrição fornecida..."}

{f"![{evidence_image.name}](/.attachments/{evidence_image.name} =300x)" if evidence_image else ""}"""
        
        st.code(exemplo, language="markdown")

if __name__ == "__main__":
    main()