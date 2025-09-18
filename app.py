import streamlit as st
import os
from PIL import Image
from agents.crew_requests import ReleaseNotesCrewAI
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Gerador de Release Notes",
    page_icon="�",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background-color: #ffffff;
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: #333333;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-top: -1rem;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #333333;
    }
    /* Reduzir espaçamento geral */
    .block-container {
        padding-top: 2rem !important;
    }
    .input-section {
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .preview-container {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #d1d5db;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .markdown-container {
        background-color: #282c34;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #3e4451;
        margin-bottom: 1rem;
        min-height: 250px;
    }
    .preview-title {
        color: #374151;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    .markdown-title {
        color: #f8f8f2;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    .sidebar-panel {
        padding: 1rem;
        margin-top: 2rem;
        text-align: center;
    }
    .version-display {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333333;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal com logo
    try:
        # Tentar carregar a logo (verificar vários formatos)
        possible_logos = ["assets/logo1.png", "assets/logo.png", "assets/logo.jpg", "assets/logo.svg"]
        logo_found = None
        
        for logo_path in possible_logos:
            if os.path.exists(logo_path):
                logo_found = logo_path
                break
        
        if logo_found:
            col_logo, col_title = st.columns([1, 5])
            with col_logo:
                # Adicionar espaço vertical para centralizar com o título
                st.markdown('<div style="margin-top: 0.8rem;"></div>', unsafe_allow_html=True)
                st.image(logo_found, width=60)
            with col_title:
                st.markdown('<h1 class="header-title">Gerador de Release Notes</h1>', unsafe_allow_html=True)
        else:
            # Fallback sem logo
            st.markdown('<div class="main-header"><h1 class="header-title">Gerador de Release Notes</h1></div>', unsafe_allow_html=True)
    except Exception as e:
        # Fallback em caso de erro
        st.markdown('<div class="main-header"><h1 class="header-title">Gerador de Release Notes</h1></div>', unsafe_allow_html=True)

    # Layout principal: conteúdo + painel lateral
    col_main, col_sidebar = st.columns([5, 1])
    
    with col_main:
        # Formulário principal
        
        # Primeira linha: Versão e Tipo
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Buscar versões existentes
            try:
                crew = ReleaseNotesCrewAI()
                existing_versions = crew.db.get_all_versions()
                version_options = ["Nova versão..."] + [v[1] for v in existing_versions]  # v[1] é o version_name
            except:
                version_options = ["Nova versão..."]
            
            # Selectbox para escolher versão existente ou criar nova
            selected_option = st.selectbox(
                "Versão da Release:",
                options=version_options,
                help="Selecione uma versão existente ou 'Nova versão...' para criar"
            )
            
            # Se escolheu "Nova versão...", mostrar campo de texto
            if selected_option == "Nova versão...":
                version_name = st.text_input(
                    "Nome da nova versão:",
                    placeholder="Ex: v4.21.0",
                    help="Digite o nome da nova versão"
                )
                
                # Validar formato da versão
                if version_name and not version_name.startswith('v'):
                    version_name = f"v{version_name}"
                    st.caption(f"Formatado como: **{version_name}**")
            else:
                # Usar versão selecionada
                version_name = selected_option
        
        with col2:
            # Tipo da task
            tipo_task = st.selectbox(
                "Tipo da Task:",
                options=["História", "Bug"],
                help="História = nova funcionalidade | Bug = correção"
            )
        
        # Segunda linha: ID da task
        col3, col4 = st.columns([1, 1])
        
        with col3:
            # ID da task (apenas números)
            task_number = st.text_input(
                "ID da Task:",
                placeholder="Ex: 3048",
                help="Digite apenas o número (será formatado como JBSV-XXXX)"
            )
            
            # Formatar o ID automaticamente
            if task_number and task_number.isdigit():
                jira_task_id = f"JBSV-{task_number}"
                st.caption(f"Formatado como: **{jira_task_id}**")
            else:
                jira_task_id = ""
                if task_number:
                    st.error("Digite apenas números")
        
        with col4:
            # Espaço para futuras funcionalidades ou deixar vazio
            st.empty()
        
        # Terceira linha: Título e Descrição
        jira_task_title = st.text_input(
            "Título da Task:",
            placeholder="Ex: Atualizar gráfico de classes ao realizar filtros",
            help="Título descritivo da funcionalidade ou correção"
        )
        
        jira_task_description = st.text_area(
            "Descrição da Task:",
            placeholder="Descreva detalhadamente o que foi implementado ou corrigido...",
            height=100,
            help="Descrição técnica detalhada que será usada para gerar a release note"
        )
        
        # Upload de evidência
        evidence_image = st.file_uploader(
            "Upload de Evidência (Opcional):",
            type=['png', 'jpg', 'jpeg', 'gif'],
            help="Imagem que demonstra a funcionalidade implementada"
        )
        
        # Mostrar preview da imagem se foi feito upload
        if evidence_image is not None:
            st.image(evidence_image, caption="Preview da imagem", width=300)
        
        # Botões de ação
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            generate_preview_button = st.button(
                "Gerar Preview",
                disabled=not (jira_task_id and jira_task_title and jira_task_description and version_name.strip()),
                help="Gera um preview da descrição que você pode editar antes de adicionar",
                use_container_width=True
            )
        
        with col_btn2:
            # Este botão só aparece quando há um preview gerado
            if 'generated_preview' in st.session_state and st.session_state.generated_preview:
                confirm_button = st.button(
                    "Confirmar e Adicionar",
                    help="Adiciona a task editada às release notes",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.button(
                    "Confirmar e Adicionar", 
                    disabled=True, 
                    help="Primeiro gere um preview",
                    use_container_width=True
                )
        
        # === ÁREA DE PREVIEW E EDIÇÃO ===
        
        # Gerar Preview
        if generate_preview_button:
            try:
                with st.spinner("Gerando preview da descrição..."):
                    # Preparar dados da task
                    task_data = {
                        "tipo_task": tipo_task,
                        "jira_task_id": jira_task_id,
                        "jira_task_title": jira_task_title,
                        "jira_task_description": jira_task_description,
                        "evidence_image": evidence_image.name if evidence_image else None
                    }
                    
                    # Gerar apenas a descrição simples
                    crew = ReleaseNotesCrewAI()
                    generated_description = crew.generate_simple_description(task_data)
                    
                    # Armazenar no session_state
                    st.session_state.generated_preview = generated_description
                    st.session_state.current_task_data = task_data
                    st.session_state.current_version = version_name.strip()
                    
                    st.success("Preview gerado! Você pode editar a descrição abaixo.")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Erro ao gerar preview: {str(e)}")
        
        # Mostrar área de edição se há preview
        if 'generated_preview' in st.session_state and st.session_state.generated_preview:
            st.markdown("---")
            st.markdown("### Edite a Descrição Gerada")
            
            # Campo editável com a descrição gerada
            edited_description = st.text_area(
                "Descrição da funcionalidade/correção:",
                value=st.session_state.generated_preview,
                height=120,
                help="Edite a descrição conforme necessário antes de adicionar às release notes"
            )
            
            # Preview da release note completa em duas colunas
            if edited_description.strip():
                # Recuperar dados da task do session_state
                task_data = st.session_state.current_task_data
                task_id = task_data['jira_task_id']
                task_title = task_data['jira_task_title']
                
                image_info = ""
                if evidence_image:
                    image_info = f"\\n![{evidence_image.name}](/.attachments/{evidence_image.name} =300x)"
                
                preview_markdown = f"###[{task_id}] {task_title}\\n\\n{edited_description.strip()}{image_info}\\n\\n---"
                
                # Layout lado a lado: Markdown | Preview
                col_md, col_preview = st.columns([1, 1])
                
                with col_md:
                    st.markdown('<div class="markdown-title">Código Markdown</div>', unsafe_allow_html=True)
                    st.code(preview_markdown, language="markdown")
                
                with col_preview:
                    st.markdown('<div class="preview-title">Preview Renderizado</div>', unsafe_allow_html=True)
                    
                    # Renderizar o título e descrição diretamente
                    st.markdown(f"### [{task_id}] {task_title}")
                    st.markdown(edited_description.strip())
                    
                    # Mostrar a imagem se existir
                    if evidence_image:
                        st.image(evidence_image, caption=evidence_image.name, width=300)
                    
                    st.markdown("---")
            
            # Armazenar descrição editada
            st.session_state.edited_description = edited_description
        
        # Confirmar e adicionar
        if 'generated_preview' in st.session_state and st.session_state.generated_preview and confirm_button:
            try:
                with st.spinner("Adicionando task às release notes..."):
                    # Usar a descrição editada
                    edited_desc = st.session_state.get('edited_description', st.session_state.generated_preview)
                    task_data = st.session_state.current_task_data
                    version_name = st.session_state.current_version
                    
                    # Preparar informação da imagem
                    image_info = ""
                    if evidence_image:
                        image_info = f"\\n![{evidence_image.name}](/.attachments/{evidence_image.name} =300x)"
                    
                    # Criar release note final
                    final_release_note = f"###[{task_data['jira_task_id']}] {task_data['jira_task_title']}\\n\\n{edited_desc.strip()}{image_info}\\n\\n---"
                    
                    # Adicionar ao banco colaborativo
                    crew = ReleaseNotesCrewAI()
                    crew.db.add_task(task_data, final_release_note, version_name)
                    
                    # Gerar markdown colaborativo atualizado
                    collaborative_markdown = crew.db.generate_collaborative_markdown(version_name)
                    
                    # Limpar session state
                    del st.session_state.generated_preview
                    del st.session_state.current_task_data
                    del st.session_state.current_version
                    if 'edited_description' in st.session_state:
                        del st.session_state.edited_description
                    
                    # Exibir resultado colaborativo
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Task Adicionada com Sucesso!")
                    st.success(f"Task {jira_task_id} foi adicionada à versão {version_name}!")
                    
                    # Mostrar estatísticas atualizadas da versão
                    stats = crew.get_version_stats(version_name)
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Total de Tasks", stats['total'])
                    with col_stat2:
                        st.metric("Histórias", stats['historias'])
                    with col_stat3:
                        st.metric("Bugs", stats['bugs'])
                    
                    st.markdown(f"### Release Notes da Versão {version_name}:")
                    st.code(collaborative_markdown, language="markdown")
                    
                    # Botão de download da versão específica
                    st.download_button(
                        label=f"Baixar Release Notes {version_name}",
                        data=collaborative_markdown,
                        file_name=f"release_notes_{version_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown"
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Forçar rerun para atualizar a interface
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Erro ao adicionar task: {str(e)}")
                st.info("Verifique sua configuração da API")
        else:
            # Não mostrar mais as release notes atuais automaticamente
            pass
    
    # Painel lateral direito
    with col_sidebar:
        st.markdown("#### Versões")
        
        # Buscar todas as versões do banco
        try:
            crew = ReleaseNotesCrewAI()
            # Vou criar uma função para listar versões na crew_requests.py
            versions = crew.db.get_all_versions()
            
            if versions:
                for version_data in versions:
                    version_name_db = version_data[1]  # version_name
                    created_at = version_data[2]  # created_at
                    
                    # Tentar gerar o link de download para cada versão
                    try:
                        current_markdown = crew.get_collaborative_release_notes(version_name_db)
                        
                        if current_markdown and "Nenhuma task adicionada ainda" not in current_markdown:
                            # Criar link de download
                            import base64
                            b64 = base64.b64encode(current_markdown.encode()).decode()
                            filename = f"release_notes_{version_name_db}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                            
                            # Mostrar versão e download na mesma linha
                            download_link = f'<a href="data:text/markdown;base64,{b64}" download="{filename}" style="color: #0066cc; text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'">Download</a>'
                            
                            # Versão com destaque se é a atual sendo editada
                            if 'version_name' in locals() and version_name and version_name.strip() == version_name_db:
                                version_html = f'<div style="font-weight: 600; margin-bottom: 8px;">{version_name_db} {download_link}</div>'
                            else:
                                version_html = f'<div style="font-weight: 600; margin-bottom: 8px;">{version_name_db} {download_link}</div>'
                            
                            st.markdown(version_html, unsafe_allow_html=True)
                        else:
                            # Versão sem download (vazia)
                            if 'version_name' in locals() and version_name and version_name.strip() == version_name_db:
                                st.markdown(f'<div style="font-weight: 600; margin-bottom: 8px;">{version_name_db} <span style="color: #999;">_Vazia_</span></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div style="font-weight: 600; margin-bottom: 8px;">{version_name_db} <span style="color: #999;">_Vazia_</span></div>', unsafe_allow_html=True)
                    except:
                        # Erro ao carregar
                        st.markdown(f'<div style="font-weight: 600; margin-bottom: 8px;">{version_name_db} <span style="color: #999;">_..._</span></div>', unsafe_allow_html=True)
                    
                    # Pequeno espaço entre versões
                    st.markdown("")
            else:
                st.write("_Nenhuma versão criada ainda_")
                
        except Exception as e:
            st.write("_Carregando versões..._")

if __name__ == "__main__":
    main()