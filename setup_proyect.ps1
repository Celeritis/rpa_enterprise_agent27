<#
.SYNOPSIS
    Script de configuración inicial para RPA Enterprise Agent
.DESCRIPTION
    Crea la estructura de directorios, archivos de configuración y
    archivos centinela para el proyecto RPA Enterprise Agent.
.NOTES
    Autor: Equipo de Desarrollo RPA
    Fecha: 27 de julio de 2026
    Versión: 1.0
#>

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "RPA ENTERPRISE AGENT - CONFIGURACION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# PASO 1: CREAR ESTRUCTURA DE DIRECTORIOS
# ============================================
Write-Host "[1/5] Creando estructura de directorios..." -ForegroundColor Yellow

$directories = @(
    "core",
    "apps/x2goclient_erp_legacy/assets",
    "apps/sap_b1/assets",
    "data/input",
    "data/output/evidences",
    "data/logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Existente: $dir" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================
# PASO 2: CREAR ARCHIVOS CENTINELA (.gitkeep)
# ============================================
Write-Host "[2/5] Creando archivos centinela (.gitkeep)..." -ForegroundColor Yellow

$gitkeepFiles = @(
    "data/input/.gitkeep",
    "data/output/evidences/.gitkeep",
    "data/logs/.gitkeep",
    "apps/x2goclient_erp_legacy/assets/.gitkeep",
    "apps/sap_b1/assets/.gitkeep"
)

foreach ($file in $gitkeepFiles) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "  Creado: $file" -ForegroundColor Green
    } else {
        Write-Host "  Existente: $file" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================
# PASO 3: CREAR .gitignore
# ============================================
Write-Host "[3/5] Creando archivo .gitignore..." -ForegroundColor Yellow

$gitignoreContent = @"
# Entornos virtuales
.venv/
venv/
env/

# Cache de Python
__pycache__/
*.py[cod]
*.pyc
.pytest_cache/

# Configuraciones de IDE
.vscode/
.idea/

# Archivos de sistema
Thumbs.db
.DS_Store

# Salidas y evidencias pesadas del RPA
data/output/evidences/*
!data/output/evidences/.gitkeep
data/logs/*
!data/logs/.gitkeep

# Archivos locales sensibles
*.local.json

# Archivos de datos de entrada
data/input/*.csv
data/input/*.xlsx
data/input/*.xls

# Archivos temporales
*.tmp
*.temp
*.log
*.bak
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8 -Force
Write-Host "  Creado: .gitignore" -ForegroundColor Green
Write-Host ""

# ============================================
# PASO 4: CREAR requirements.txt
# ============================================
Write-Host "[4/5] Creando archivo requirements.txt..." -ForegroundColor Yellow

$requirementsContent = @"
opencv-python>=4.8.0
pyautogui>=0.9.54
pygetwindow>=0.0.9
pytesseract>=0.3.10
pyperclip>=1.8.2
Pillow>=10.0.0
numpy>=1.24.0
"@

$requirementsContent | Out-File -FilePath "requirements.txt" -Encoding UTF8 -Force
Write-Host "  Creado: requirements.txt" -ForegroundColor Green
Write-Host ""

# ============================================
# PASO 5: CREAR README.md
# ============================================
Write-Host "[5/5] Creando archivo README.md..." -ForegroundColor Yellow

$readmeContent = @"
# RPA Enterprise Agent

Motor de automatizacion RPA agnostico disenado para interactuar con aplicaciones de escritorio (X2GoClient, SAP B1, etc.) mediante vision artificial (OpenCV) y control de inputs robusto.

## Estructura del Proyecto
- core/: Motor de ejecucion (Vision, Inputs, Ventanas, Esperas)
- apps/: Configuraciones especificas y assets por aplicacion
- data/: Entradas, salidas, logs y evidencias

## Instalacion

### 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/rpa_enterprise_agent27.git
cd rpa_enterprise_agent27

### 2. Crear entorno virtual
python -m venv .venv

### 3. Activar entorno virtual
- Windows: .venv\Scripts\activate
- Linux/Mac: source .venv/bin/activate

### 4. Instalar dependencias
pip install -r requirements.txt

## Uso
python main.py

## Caracteristicas
- Vision artificial con OpenCV
- Control de teclado y raton
- Gestion de ventanas
- Esperas inteligentes
- Multiples aplicaciones soportadas

## Contribucion
1. Fork el repositorio
2. Crear rama feature (git checkout -b feature/nueva-funcionalidad)
3. Commit cambios (git commit -m 'Añadir nueva funcionalidad')
4. Push a la rama (git push origin feature/nueva-funcionalidad)
5. Crear Pull Request

## Licencia
MIT
"@

$readmeContent | Out-File -FilePath "README.md" -Encoding UTF8 -Force
Write-Host "  Creado: README.md" -ForegroundColor Green
Write-Host ""

# ============================================
# COMPLETADO
# ============================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CONFIGURACION COMPLETADA" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Estructura creada:" -ForegroundColor White
Write-Host "  core/" -ForegroundColor Gray
Write-Host "  apps/x2goclient_erp_legacy/assets/" -ForegroundColor Gray
Write-Host "  apps/sap_b1/assets/" -ForegroundColor Gray
Write-Host "  data/input/" -ForegroundColor Gray
Write-Host "  data/output/evidences/" -ForegroundColor Gray
Write-Host "  data/logs/" -ForegroundColor Gray
Write-Host ""
Write-Host "Archivos creados:" -ForegroundColor White
Write-Host "  .gitignore" -ForegroundColor Gray
Write-Host "  requirements.txt" -ForegroundColor Gray
Write-Host "  README.md" -ForegroundColor Gray
Write-Host "  5 archivos .gitkeep" -ForegroundColor Gray
Write-Host ""
Write-Host "Siguientes pasos:" -ForegroundColor Yellow
Write-Host "  1. Revisar archivos creados"
Write-Host "  2. git add ."
Write-Host "  3. git commit -m 'feat: Estructura inicial del proyecto'"
Write-Host "  4. git push origin main"
Write-Host ""

# Pausa para ver resultados
Read-Host "Presiona Enter para salir..."