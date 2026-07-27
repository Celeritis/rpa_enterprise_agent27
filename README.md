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
3. Commit cambios (git commit -m 'AÃ±adir nueva funcionalidad')
4. Push a la rama (git push origin feature/nueva-funcionalidad)
5. Crear Pull Request

## Licencia
MIT
