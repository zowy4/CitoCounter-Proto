# Script de PowerShell para ejecutar la prueba de cámara o simulador sintético
$ErrorActionPreference = "Stop"
$PYTHON_EXE = "C:/Users/zowya/AppData/Local/Programs/Python/Python312/python.exe"

if (-not (Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "python"
}

Write-Host "Iniciando prueba de captura de video con CitoCounter-Proto..." -ForegroundColor Cyan
& $PYTHON_EXE probar_camara.py
