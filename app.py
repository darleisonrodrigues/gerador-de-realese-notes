import streamlit as st
import os
from datetime import datetime
from agents.crew_requests import ReleaseNotesCrewAI

# Deploy: 2025-10-01 - Interface melhorada

# Imports opcionais para evitar erros no deploy
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv não é essencial no Streamlit Cloud

# Configuração da página
st.set_page_config(
    page_title="Gerador de Release Notes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .version-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .version-row:hover {
        border-color: #007bff;
        box-shadow: 0 4px 8px rgba(0,123,255,0.15);
        transform: translateY(-1px);
    }
    .version-name {
        font-weight: 600;
        flex-grow: 1;
        margin-right: 8px;
        font-size: 0.9rem;
    }
    .version-buttons {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .version-btn {
        padding: 6px 10px;
        font-size: 0.75rem;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        min-width: 70px;
        text-align: center;
        justify-content: center;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    .edit-btn {
        background: linear-gradient(135deg, #ffc107 0%, #ffcd39 100%);
        color: #000;
        border: 1px solid #ffb302;
    }
    .edit-btn:hover {
        background: linear-gradient(135deg, #ffb302 0%, #ffc107 100%);
        transform: scale(1.05);
    }
    .download-btn {
        background: linear-gradient(135deg, #28a745 0%, #34ce57 100%);
        color: white;
        border: 1px solid #1e7e34;
    }
    .download-btn:hover {
        background: linear-gradient(135deg, #1e7e34 0%, #28a745 100%);
        transform: scale(1.05);
    }
    .delete-btn {
        background: linear-gradient(135deg, #dc3545 0%, #e85565 100%);
        color: white;
        border: 1px solid #bd2130;
        padding: 6px 8px;
        min-width: 40px;
    }
    .delete-btn:hover {
        background: linear-gradient(135deg, #bd2130 0%, #dc3545 100%);
        transform: scale(1.05);
    }
    .version-status {
        font-size: 0.7rem;
        color: #6c757d;
        font-style: italic;
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
        # === ÁREA DE EDIÇÃO DE VERSÃO EXISTENTE ===
        if 'editing_version' in st.session_state and 'editing_content' in st.session_state:
            st.markdown("---")
            st.markdown(f"### ✏️ Editando Versão: {st.session_state.editing_version}")
            
            # Campo de edição do markdown
            edited_markdown = st.text_area(
                "Conteúdo das Release Notes:",
                value=st.session_state.editing_content,
                height=300,
                help="Edite o conteúdo das release notes diretamente"
            )
            
            # Mostrar informações sobre o conteúdo
            if edited_markdown:
                lines = len(edited_markdown.split('\n'))
                chars = len(edited_markdown)
                words = len(edited_markdown.split())
                st.caption(f"📊 Estatísticas: {lines} linhas • {words} palavras • {chars} caracteres")
            else:
                st.warning("⚠️ Atenção: Conteúdo está vazio!")
            
            # Botões de ação
            col_save, col_preview, col_cancel = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("💾 Salvar Alterações", use_container_width=True):
                    try:
                        with st.spinner("Salvando alterações..."):
                            # Validar se há conteúdo
                            if not edited_markdown.strip():
                                st.error("Não é possível salvar conteúdo vazio!")
                                st.stop()
                            
                            # Salvar as alterações no banco
                            crew = ReleaseNotesCrewAI()
                            crew.db.update_version_content(st.session_state.editing_version, edited_markdown)
                            
                            # Atualizar o session state com o novo conteúdo
                            st.session_state.editing_content = edited_markdown
                        
                        st.success(f"Versão {st.session_state.editing_version} atualizada com sucesso!")
                        st.info("💡 Dica: Você pode continuar editando ou cancelar para voltar ao menu principal.")
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
                        st.info("Tente novamente ou cancele a edição")
            
            with col_preview:
                if st.button("👁️ Preview", use_container_width=True):
                    # Mostrar preview do markdown editado
                    with st.expander("Preview das Release Notes", expanded=True):
                        st.markdown(edited_markdown)
            
            with col_cancel:
                if st.button("❌ Cancelar", use_container_width=True):
                    # Cancelar edição
                    if 'editing_version' in st.session_state:
                        del st.session_state.editing_version
                    if 'editing_content' in st.session_state:
                        del st.session_state.editing_content
                    st.rerun()
            
            st.markdown("---")
            return  # Sair da função, não mostrar mais nada quando está editando
        
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
                options=["User Story", "Bug", "Improvement", "Technical Debt"],
                help="Selecione o tipo da task conforme classificação do projeto"
            )
        
        # Segunda linha: ID da task e QA Level
        col3, col4 = st.columns([1, 1])
        
        with col3:
            # ID da task (apenas números)
            task_number = st.text_input(
                "ID da Task:",
                placeholder="Ex: 3048",
                help="Digite apenas o número (será formatado como JBSV-XXXX)"
            )
        
        with col4:
            # QA Level
            qa_level = st.selectbox(
                "QA Level:",
                options=[0, 1, 2, 3],
                help="Selecione o nível de QA da task"
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
        
        # Terceira linha: Título e Link TFS
        jira_task_title = st.text_input(
            "Título da Task:",
            placeholder="Ex: Atualizar gráfico de classes ao realizar filtros",
            help="Título descritivo da funcionalidade ou correção"
        )
        
        # Campo para Link TFS
        tfs_link = st.text_input(
            "Link da Task:",
            placeholder="Ex: https://tfs.jbs.com.br/tfs/JBSFDV/VENDA_MAIS_APP/_workitems/edit/9124",
            help="Link completo do item no TFS - será usado para criar o link clicável no título"
        )
        
        jira_task_description = st.text_area(
            "Descrição da Task:",
            placeholder="Descreva detalhadamente o que foi implementado ou corrigido...",
            height=100,
            help="Descrição técnica detalhada que será usada para gerar a release note"
        )
        
        # Botões de ação
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            generate_preview_button = st.button(
                "Gerar Preview",
                disabled=not (jira_task_id and jira_task_title and jira_task_description and version_name.strip() and qa_level is not None),
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
                        "qa_level": qa_level,
                        "tfs_link": tfs_link
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
                qa_level = task_data['qa_level']
                tfs_link = task_data.get('tfs_link')
                
                # Criar título com ou sem link
                if tfs_link:
                    title_formatted = f"###[[{task_id}] {task_title}]({tfs_link})"
                else:
                    title_formatted = f"###[{task_id}] {task_title}"
                
                # Linha QA Level
                qa_line = f"\n\n**QA Level: {qa_level}**\n\n"
                
                preview_markdown = f"{title_formatted}{qa_line}{edited_description.strip()}\n\n---"
                
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
                    
                    # Criar título com ou sem link TFS
                    if task_data.get('tfs_link'):
                        title_formatted = f"###[[{task_data['jira_task_id']}] {task_data['jira_task_title']}]({task_data['tfs_link']})"
                    else:
                        title_formatted = f"###[{task_data['jira_task_id']}] {task_data['jira_task_title']}"
                    
                    # Linha QA Level
                    qa_line = f"\n\n**QA Level: {task_data['qa_level']}**\n\n"
                    
                    # Criar release note final
                    final_release_note = f"{title_formatted}{qa_line}{edited_desc.strip()}\n\n---"
                    
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
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    with col_stat1:
                        st.metric("Total de Tasks", stats['total'])
                    with col_stat2:
                        st.metric("User Stories", stats['user_stories'])
                    with col_stat3:
                        st.metric("Bugs", stats['bugs'])
                    with col_stat4:
                        st.metric("Improvements", stats['improvements'])
                    
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
                            
                            # Layout horizontal da versão com botões
                            version_color = "#0066cc" if 'version_name' in locals() and version_name and version_name.strip() == version_name_db else "#333"
                            
                            # Container da versão com layout horizontal melhorado
                            version_html = f'''
                            <div class="version-row">
                                <div class="version-name" style="color: {version_color};">{version_name_db}</div>
                                <div class="version-buttons">
                                    <a href="data:text/markdown;base64,{b64}" download="{filename}" class="version-btn download-btn" title="Baixar Release Notes">
                                        📥 Download
                                    </a>
                                </div>
                            </div>
                            '''
                            
                            st.markdown(version_html, unsafe_allow_html=True)
                            
                            # Botões de ação em colunas
                            col_edit, col_delete = st.columns([1, 1])
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_{version_name_db}", help="Editar esta versão", use_container_width=True):
                                    st.session_state.editing_version = version_name_db
                                    st.session_state.editing_content = current_markdown
                                    st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️ Excluir", key=f"delete_{version_name_db}", help="Excluir esta versão", use_container_width=True, type="secondary"):
                                    try:
                                        crew = ReleaseNotesCrewAI()
                                        crew.db.delete_version(version_name_db)
                                        st.success(f"Versão {version_name_db} excluída com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {str(e)}")
                        else:
                            # Versão sem download (vazia)
                            version_color = "#0066cc" if 'version_name' in locals() and version_name and version_name.strip() == version_name_db else "#333"
                            
                            version_html = f'''
                            <div class="version-row">
                                <div class="version-name" style="color: {version_color};">{version_name_db}</div>
                                <div class="version-status">_Vazia_</div>
                            </div>
                            '''
                            
                            st.markdown(version_html, unsafe_allow_html=True)
                            
                            # Botões de ação em colunas
                            col_edit, col_delete = st.columns([1, 1])
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_empty_{version_name_db}", help="Editar esta versão", use_container_width=True):
                                    st.session_state.editing_version = version_name_db
                                    st.session_state.editing_content = "# Release Notes\n\nAdicione o conteúdo das release notes aqui..."
                                    st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️ Excluir", key=f"delete_empty_{version_name_db}", help="Excluir esta versão", use_container_width=True, type="secondary"):
                                    try:
                                        crew = ReleaseNotesCrewAI()
                                        crew.db.delete_version(version_name_db)
                                        st.success(f"Versão {version_name_db} excluída com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {str(e)}")
                    except:
                        # Erro ao carregar - mostrar versão simples com botões de ação
                        version_html = f'''
                        <div class="version-row">
                            <div class="version-name">{version_name_db}</div>
                            <div class="version-status">_Erro ao carregar_</div>
                        </div>
                        '''
                        
                        st.markdown(version_html, unsafe_allow_html=True)
                        
                        # Botões de ação em colunas
                        col_edit, col_delete = st.columns([1, 1])
                        
                        with col_edit:
                            if st.button("✏️ Editar", key=f"edit_error_{version_name_db}", help="Editar esta versão", use_container_width=True):
                                st.session_state.editing_version = version_name_db
                                st.session_state.editing_content = "# Release Notes\n\nAdicione o conteúdo das release notes aqui..."
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Excluir", key=f"delete_error_{version_name_db}", help="Excluir esta versão", use_container_width=True, type="secondary"):
                                try:
                                    crew = ReleaseNotesCrewAI()
                                    crew.db.delete_version(version_name_db)
                                    st.success(f"Versão {version_name_db} excluída com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {str(e)}")
                    
                    # Pequeno espaço entre versões
                    st.markdown("")
            else:
                st.write("_Nenhuma versão criada ainda_")
                
        except Exception as e:
            st.write("_Carregando versões..._")

if __name__ == "__main__":
    main()