# Gerador Automático de Release Notes Colaborativo

Sistema colaborativo para geração automática de release notes usando Stre## 💾 Sistema de Versionamento

- **Isolamento por Versão** - Cada versão m## ✅ Vantagens da Versão Atual

✅ **Interface Profissional** - Design limpo 
✅ **Colaborativo Real** - Múltiplos devs, múltiplas versões
✅ **Preview Editável** - Controle total sobre o conteúdo gerado
✅ **Versionamento Inteligente** - Isolamento automático entre versões
✅ **Downloads Organizados** - Acesso direto a qualquer versão
✅ **Sem Criação Prematura** - Versões só existem com conteúdo
✅ **Persistência Confiável** - SQLite local com backup automático
✅ **IA Otimizada** - Modelo deepseek para melhor qualidade
✅ **Economia de Recursos** - API calls apenas quando necessário
✅ **UX Melhorada** - Fluxo intuitivo e eficienteks separadas
- **Criação Sob Demanda** - Versões só existem quando têm conteúdo
- **Dropdown Inteligente** - Seleciona versões existentes ou cria novas
- **Painel de Versões** - Lista todas as versões com downloads diretos
- **Persistência SQLite** - Banco local com histórico completo CrewAI. **Múltiplos desenvolvedores podem trabalhar na mesma versão simultaneamente!**

## ✨ Funcionalidades Principais

- **🏢 Sistema Colaborativo** - Múltiplos desenvolvedores, uma versão
- **📦 Gerenciamento de Versões** - Isolamento automático entre versões
- **🤖 IA Inteligente** - Groq API (deepseek-r1-distill-llama-70b)
- **👁️ Preview em Tempo Real** - Edição lado a lado com preview markdown
- **💾 Persistência Automática** - SQLite com histórico completo
- **📱 Interface Limpa** - Design profissional sem emojis excessivos
- **⬇️ Downloads Organizados** - Links diretos para cada versão
- **🔄 Seleção de Versões** - Dropdown inteligente para reutilizar versões

## 📋 Pré-requisitos

- Python 3.8+
- Groq API Key (gratuita: https://console.groq.com)
- Git (opcional)

## 🛠️ Instalação Rápida

1. **Execute o setup automático (Windows):**
```cmd
cd release-notes-generator
setup.bat
```

2. **Configure sua Groq API Key:**
   - Obtenha gratuitamente em: https://console.groq.com
   - Cole na interface ou configure no arquivo `.env`

3. **Inicie a aplicação:**
```cmd
run.bat
```

## 📖 Instalação Manual

1. **Clone ou baixe o projeto:**
```cmd
git clone <seu-repositorio>
cd release-notes-generator
```

2. **Crie um ambiente virtual:**
```cmd
python -m venv venv
venv\Scripts\activate
```

3. **Instale as dependências:**
```cmd
pip install -r requirements.txt
```

4. **Inicie a aplicação:**
```cmd
streamlit run app.py
```

## 🎯 Como Usar (Fluxo Colaborativo Atualizado)

### 1. **Configuração da Versão**
- **Seleção Inteligente**: Use o dropdown para escolher versão existente ou criar nova
- **Isolamento Automático**: Cada versão mantém suas tasks separadas
- **Não há criação prematura**: Versões só são criadas ao adicionar a primeira task

### 2. **Adicionando Tasks**
- **Formulário Limpo**: Preencha tipo, ID, título e descrição da task
- **Upload de Evidência**: Adicione imagens quando necessário
- **Preview Editável**: 
  1. Clique "Gerar Preview" para ver descrição gerada pela IA
  2. Edite o texto no campo lado a lado com preview markdown
  3. Clique "Confirmar e Adicionar" para salvar

### 3. **Gerenciamento por Versão**
- **Painel Lateral**: Visualize todas as versões criadas
- **Downloads Diretos**: "v4.21.0 Download" - links diretos para cada versão


### 4. **Workflow Otimizado**
```
Digite/Selecione Versão → Preenche Task → Gera Preview → 
Edita Descrição → Confirma → Task Salva na Versão
```

## 📁 Estrutura do Projeto

```
release-notes-generator/
│
├── app.py                     # Interface principal Streamlit (layout wide, sem emojis)
├── requirements.txt           # Dependências (Groq + Streamlit)
├── .env                      # Configurações de API (criar manualmente)
├── setup.bat / run.bat       # Scripts Windows
├── README.md                 # Este arquivo
│
├── agents/                   # Sistema IA
│   ├── __init__.py
│   └── crew_requests.py      # API Groq (deepseek-r1-distill-llama-70b)
│
├── database/                # Persistência
│   ├── __init__.py
│   ├── collaborative_db.py  # Gerenciamento SQLite com isolamento de versões
│   └── collaborative.db     # Banco SQLite (criado automaticamente)
│
└── examples/                # Imagens e exemplos
```

## 🤖 Sistema IA Simplificado

### Modelo Único Otimizado
- **deepseek-r1-distill-llama-70b** - Modelo avançado da Groq
- **API Direta** - Requests HTTP simples e eficiente
- **Geração Inteligente** - Transforma descrições técnicas em linguagem clara
- **Limpeza Automática** - Remove formatação desnecessária

### Processamento
1. **Entrada**: Dados da task (tipo, ID, título, descrição)
2. **IA**: Gera descrição focada no usuário final
3. **Edição**: Preview lado a lado para ajustes
4. **Saída**: Markdown otimizado para Azure DevOps

## � Sistema de Persistência

- **Banco SQLite** para armazenar todas as entries
- **Múltiplos desenvolvedores** podem trabalhar na mesma sprint
- **Histórico completo** de todas as alterações
- **Backup automático** dos dados
- **Recuperação fácil** de entries anteriores

## � Formato de Saída Final

O sistema compila automaticamente:

```markdown
[[TOC]]

## História
###[JBSV-XXXX] Funcionalidade 1
Conteúdo gerado pela IA...
![imagem1.png](/.attachments/imagem1.png =300x)
---

###[JBSV-YYYY] Funcionalidade 2
Conteúdo gerado pela IA...
---

## Bug
###[JBSV-ZZZZ] Correção 1
Conteúdo gerado pela IA...
---
```

## 🔧 Configurações Técnicas

### Groq API
- **Modelo**: deepseek-r1-distill-llama-70b
- **Configuração**: Arquivo `.env` ou interface
- **Custo**: Economico comparado a OpenAI

### Banco de Dados
- **SQLite**: `database/collaborative.db`
- **Tabelas**: `release_versions`, `tasks`
- **Reset**: Use função `clear_database()` se necessário

### Interface
- **Layout**: Wide mode para melhor aproveitamento
- **CSS**: Estilos customizados para links de download
- **Responsivo**: Funciona em diferentes resoluções

## 🎯 Fluxo de Trabalho Otimizado

1. **Setup Inicial:**
   ```
   Configura Groq API → Acessa Interface Limpa
   ```

2. **Por Desenvolvedor:**
   ```
   Seleciona/Cria Versão → Preenche Task → Gera Preview → 
   Edita Descrição → Confirma → Download Disponível
   ```

3. **Por Versão:**
   ```
   v4.21.0 Download → v4.22.0 Download → v4.23.0 Download
   (Painel lateral organizado)
   ```

4. **Colaboração:**
   ```
   Dev1 adiciona tasks → Dev2 adiciona tasks → 
   Ambos usam mesma versão → Download unificado
   ```

## � Vantagens

✅ **Colaborativo** - Múltiplos devs, uma sprint
✅ **Persistente** - Nada se perde
✅ **Inteligente** - IA aprende com exemplos
✅ **Econômico** - Groq é mais barato
✅ **Rápido** - Interface otimizada
✅ **Padronizado** - Formato consistente
✅ **Flexível** - Salva rascunhos ou gera IA

## � Solução de Problemas

1. **API Key Inválida**: 
   - Verifique em: https://console.groq.com
   - Configure no arquivo `.env` ou interface

2. **Versão não aparece**: 
   - Certifique-se de confirmar a task (não apenas gerar preview)
   - Versões só são criadas ao adicionar primeira task

3. **Preview não carrega**: 
   - Verifique conexão com internet
   - Tente novamente após alguns segundos

4. **Banco corrompido**: 
   - Delete o arquivo `database/collaborative.db`
   - Sistema recriará automaticamente

5. **Interface lenta**:
   - Use modelo deepseek (padrão)
   - Evite descriptions muito longas



## 🔄 Próximas Melhorias

- [ ] **Edição de Tasks Existentes** - Modificar tasks já salvas
- [ ] **Histórico de Mudanças** - Auditoria de modificações
- [ ] **Templates de Versão** - Modelos pré-configurados
- [ ] **Exportação Multi-formato** - Word, HTML, etc.
- [ ] **Integração Jira** - Import automático de tasks
- [ ] **Colaboração em Tempo Real** - WebSocket updates
- [ ] **Roles e Permissões** - Admin, Developer, Viewer
- [ ] **Notificações** - Alerts para novas tasks

---
