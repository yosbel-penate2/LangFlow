import os
import sys
from pathlib import Path

# 1. Obtener ruta absoluta de la carpeta custom
current_dir = Path(__file__).parent.absolute()
CUSTOM_PATH = current_dir / "custom"

# 2. Asegurar que existe
CUSTOM_PATH.mkdir(exist_ok=True)

# 3. FORZAR la variable de entorno (esto es clave)
os.environ["LANGFLOW_COMPONENTS_PATH"] = str(CUSTOM_PATH)

# 4. También añadir al Python path
sys.path.insert(0, str(CUSTOM_PATH))

print(f"🚀 Iniciando LangFlow 1.7.2")
print(f"📁 Componentes en: {CUSTOM_PATH}")
print(f"🔧 Variable: {os.getenv('LANGFLOW_COMPONENTS_PATH')}")

# 5. Verificar estructura
print("\n📋 Verificando estructura:")
for file in CUSTOM_PATH.iterdir():
    print(f"  - {file.name}")

# 6. Importar y ejecutar LangFlow
try:
    from langflow import run
    run(
        host="127.0.0.1",
        port=7860,
        components_path=str(CUSTOM_PATH),
        log_level="debug"
    )
except ImportError:
    # Método alternativo
    os.system(f"langflow run --host 127.0.0.1 --port 7860 --log-level debug")