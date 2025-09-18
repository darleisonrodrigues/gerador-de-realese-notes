@echo off
echo ========================================
echo  Gerador de Release Notes - Setup
echo ========================================
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo [1/4] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate

echo [3/4] Instalando dependências...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependências
    pause
    exit /b 1
)

echo [4/4] Criando arquivo de configuração...
if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANTE: Configure sua OpenAI API Key no arquivo .env
    echo.
)

echo.
echo ========================================
echo  Setup concluído com sucesso!
echo ========================================
echo.
echo Para iniciar a aplicação:
echo   1. venv\Scripts\activate
echo   2. streamlit run app.py
echo.
echo Não esqueça de configurar sua OpenAI API Key!
echo.
pause