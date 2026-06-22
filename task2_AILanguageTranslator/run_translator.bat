@echo off
setlocal

set "APP_DIR=%~dp0"
set "CONDA_ROOT=%USERPROFILE%\anaconda3"
set "PYTHON_EXE=%CONDA_ROOT%\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python was not found at "%PYTHON_EXE%".
    echo Install Python or update this launcher to point to your Python executable.
    pause
    exit /b 1
)

set "PATH=%CONDA_ROOT%;%CONDA_ROOT%\Library\bin;%CONDA_ROOT%\Scripts;%PATH%"
set "TCL_LIBRARY=%CONDA_ROOT%\envs\oldenv\tcl\tcl8.6"
set "TK_LIBRARY=%CONDA_ROOT%\envs\oldenv\tcl\tk8.6"

cd /d "%APP_DIR%"
"%PYTHON_EXE%" main.py

if errorlevel 1 (
    echo.
    echo The app closed with an error.
    pause
)
