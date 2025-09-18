import os
import streamlit as st
from pathlib import Path
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import tempfile
import pickle

class DocumentProcessor:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.documents = []
        self.vector_store_path = "rag/vector_store"
        
    def initialize_embeddings(self):
        """Inicializa as embeddings do Hugging Face (gratuitas)"""
        if not self.embeddings:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
    
    def extract_text_from_pdf(self, pdf_file):
        """Extrai texto de um arquivo PDF"""
        try:
            # Se for um arquivo do Streamlit
            if hasattr(pdf_file, 'read'):
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            else:
                # Se for um caminho de arquivo
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            st.error(f"Erro ao extrair texto do PDF: {str(e)}")
            return ""
    
    def split_text(self, text, chunk_size=1000, chunk_overlap=200):
        """Divide o texto em chunks menores"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_text(text)
    
    def create_documents(self, text_chunks, source="PDF"):
        """Cria documentos Langchain a partir dos chunks de texto"""
        documents = []
        for i, chunk in enumerate(text_chunks):
            doc = Document(
                page_content=chunk,
                metadata={"source": source, "chunk": i}
            )
            documents.append(doc)
        return documents
    
    def process_pdf(self, pdf_file):
        """Processa um PDF completo"""
        try:
            self.initialize_embeddings()
            
            # Extrair texto
            text = self.extract_text_from_pdf(pdf_file)
            if not text.strip():
                st.warning("Nenhum texto encontrado no PDF")
                return False
            
            # Dividir em chunks
            chunks = self.split_text(text)
            
            # Criar documentos
            docs = self.create_documents(chunks, source=pdf_file.name if hasattr(pdf_file, 'name') else "PDF")
            self.documents.extend(docs)
            
            # Criar ou atualizar vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(docs, self.embeddings)
            else:
                # Adicionar novos documentos ao vector store existente
                new_vector_store = FAISS.from_documents(docs, self.embeddings)
                self.vector_store.merge_from(new_vector_store)
            
            # Salvar vector store
            self.save_vector_store()
            
            return True
            
        except Exception as e:
            st.error(f"Erro ao processar PDF: {str(e)}")
            return False
    
    def save_vector_store(self):
        """Salva o vector store no disco"""
        try:
            os.makedirs("rag", exist_ok=True)
            self.vector_store.save_local(self.vector_store_path)
            
            # Salvar também os documentos
            with open("rag/documents.pkl", "wb") as f:
                pickle.dump(self.documents, f)
                
        except Exception as e:
            st.error(f"Erro ao salvar vector store: {str(e)}")
    
    def load_vector_store(self):
        """Carrega o vector store do disco"""
        try:
            self.initialize_embeddings()
            
            if os.path.exists(self.vector_store_path):
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
                # Carregar documentos
                if os.path.exists("rag/documents.pkl"):
                    with open("rag/documents.pkl", "rb") as f:
                        self.documents = pickle.load(f)
                
                return True
            return False
            
        except Exception as e:
            st.error(f"Erro ao carregar vector store: {str(e)}")
            return False
    
    def search_similar_content(self, query, k=3):
        """Busca conteúdo similar no vector store"""
        try:
            if self.vector_store is None:
                if not self.load_vector_store():
                    return []
            
            # Buscar documentos similares
            similar_docs = self.vector_store.similarity_search(query, k=k)
            
            return [doc.page_content for doc in similar_docs]
            
        except Exception as e:
            st.error(f"Erro ao buscar conteúdo similar: {str(e)}")
            return []
    
    def get_context_for_task(self, task_description, max_context_length=2000):
        """Obtém contexto relevante para uma task específica"""
        try:
            # Buscar conteúdo similar
            similar_content = self.search_similar_content(task_description)
            
            if not similar_content:
                return ""
            
            # Combinar o conteúdo encontrado
            context = "\n\n".join(similar_content)
            
            # Limitar o tamanho do contexto
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            
            return context
            
        except Exception as e:
            st.error(f"Erro ao obter contexto: {str(e)}")
            return ""

# Função para criar exemplos de release notes
def create_example_release_notes():
    """Cria exemplos de release notes para referência"""
    examples = {
        "historia_exemplo.md": """###[JBSV-3061] Módulo Supervisor

O Módulo do Supervisor chegou para facilitar a gestão do time e dar mais clareza sobre os resultados, tudo em um só lugar dentro do Venda+.

Agora, ao acessar o aplicativo com seu login, o supervisor pode selecionar o seu próprio CPF no momento do login e visualizar um painel de gerenciamento completo do time, com indicadores consolidados e também a possibilidade de detalhar vendedor por vendedor.

📊 **Visão do mês**

Logo na tela inicial, o supervisor já encontra um resumo do mês em andamento, com indicadores que mostram de forma simples como está a performance da equipe:

• Expectativa do atingimento da meta do mês do time em % até a data em questão
• Volume faturado e vendido em relação à meta
• Valor faturado e vendido em relação à meta
• Visitas e pedidos realizados
• Clientes positivados
• Classes positivadas, que mostram a diversificação dos produtos trabalhados
• Acesso ao book de execução

👥 **Acompanhamento por vendedor**

Se o supervisor quiser analisar mais a fundo, basta abrir a lista de vendedores para ver os resultados de cada um.

É possível conferir quanto cada vendedor já faturou, sua taxa de atingimento da meta, além da participação nas classes de produtos.

✅ **Um painel completo na palma da mão**

Com o Módulo do Supervisor, o Venda+ passa a ser também uma ferramenta de gestão inteligente, onde o supervisor consegue:

• Visualizar o resultado consolidado da equipe
• Acompanhar o desempenho do dia e do mês
• Avaliar classes de produtos trabalhadas
• Consultar indicadores de execução e visitas
• Analisar individualmente cada vendedor

![supervisor.png](/.attachments/supervisor.png =300x)

---""",
        
        "bug_exemplo.md": """###[JBSV-3316] PDF calculando com valor errado

Corrigimos um problema no aplicativo onde o PDF de um pedido apresentava o "valor unitário" e "preço por KG" calculados incorretamente para itens com peso variável.

🔧 **O que foi corrigido:**

O erro estava no cálculo que utilizava o valor total e o peso médio de itens com peso variável. Agora o cálculo está correto e alinhado com a informação exibida na tela de consulta.

✅ **Resultado:**

• PDFs agora mostram valores corretos para todos os tipos de produtos
• Informações consistentes entre tela e PDF
• Maior precisão nos relatórios de pedidos

---"""
    }
    
    # Criar diretório de exemplos se não existir
    os.makedirs("examples", exist_ok=True)
    
    # Salvar exemplos
    for filename, content in examples.items():
        filepath = f"examples/{filename}"
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

# Inicializar exemplos ao importar o módulo
create_example_release_notes()