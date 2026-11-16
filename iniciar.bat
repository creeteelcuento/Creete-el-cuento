@echo off
setlocal
cd /d "%~dp0"

if not exist "requirements.txt" (
    echo No se encontro requirements.txt. Ejecuta este archivo desde el repositorio Creete-el-cuento.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if %errorlevel%==0 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
    if errorlevel 1 (
        echo No se pudo crear el entorno virtual. Verifica que Python 3 este instalado.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo No se pudieron instalar las dependencias definidas en requirements.txt.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m streamlit run ".\src\lineacodigo.py"
if errorlevel 1 (
    echo La aplicacion termino con un error. Revisa los mensajes anteriores.
    pause
    exit /b 1
)

endlocal
