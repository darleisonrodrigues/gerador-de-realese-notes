@echo off
echo Iniciando Gerador de Release Notes...
echo.

:: Verificar se o ambiente virtual existe
if not exist venv\ (
    echo ERRO: Ambiente virtual não encontrado.
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

:: Ativar ambiente virtual
call venv\Scripts\activate

:: Verificar se as dependências estão instaladas
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ERRO: Dependências não instaladas.
    echo Execute setup.bat primeiro.
    pause
    exit /b 1
)

:: Iniciar aplicação
echo Abrindo aplicação no navegador...
echo Pressione Ctrl+C para parar a aplicação.
echo.
streamlit run app.py