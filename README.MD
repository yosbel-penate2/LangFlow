.venv\Scripts\activate.bat

uv run langflow run

Problema: Componente no aparece

# 1. Verifica la ruta
echo %LANGFLOW_COMPONENTS_PATH%

# 2. Reinicia LangFlow completamente
# 3. Verifica errores en consola:
langflow run --log-level debug

# 4. Verifica permisos de archivo