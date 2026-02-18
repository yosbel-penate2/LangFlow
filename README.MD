.venv\Scripts\activate.bat

uv run langflow run

Problema: Componente no aparece

# 1. Verifica la ruta
echo %LANGFLOW_COMPONENTS_PATH%

# 2. Reinicia LangFlow completamente
# 3. Verifica errores en consola:
langflow run --log-level debug

# 4. Verifica permisos de archivo

---

# 🛠 Guía de Instalación y Uso: Generador de session de Telegram con Telethon

Este proyecto utiliza [Telethon](https://docs.telethon.dev/) para interactuar con la API de Telegram. Incluye herramientas para generar una `session_string`, esencial para autenticar clientes sin necesidad de iniciar sesión cada vez.

---

## ✅ Requisitos Previos

- Python 3.8 o superior
- Git (opcional)
- Cuenta de Telegram activa
- Acceso a [my.telegram.org](https://my.telegram.org) para obtener tus credenciales

---

## 🔧 Instalación

### 1. Clona el repositorio (si aplica)

```bash
git clone https://github.com/tu-usuario/tu-proyecto.git
cd tu-proyecto


2. Crea un entorno virtual (recomendado)
bash
python -m venv venv
En Windows:

cmd
venv\Scripts\activate
En macOS/Linux:

bash
source venv/bin/activate
3. Instala las dependencias
bash
pip install telethon python-dotenv

1. Crea el archivo .env
Crea un archivo llamado .env en la raíz del proyecto con este contenido:

env
API_ID=1234560
API_HASH=abcdef1234567890abcdef

🔐 Reemplaza los valores con los tuyos obtenidos de https://my.telegram.org
❗ Nunca subas este archivo a GitHub. Está protegido por .gitignore.

🪄 Generar tu Session String
La session_string es tu credencial de acceso. Guárdala con cuidado.

1. Ejecuta el script
bash
python generate_session_string.py

2. Sigue las instrucciones
Ingresa tu número de teléfono con código de país (ej: +521234567890)
Recibirás un código SMS o llamada
Introduce el código cuando te lo pida
El sistema generará tu session_string

3. Resultado
Verás un mensaje como:

🔐 TU STRING SESSION (GUÁRDALO SEGURO):
--------------------------------------------------
1BQAmXMB32...abcdef1234567890...
--------------------------------------------------
✅ También se guarda automáticamente en tus Mensajes Guardados de Telegram.

💾 ¿Cómo usar la session_string?

⚠️ Seguridad
❌ NUNCA compartas tu session_string. Es como darle acceso completo a tu cuenta.
❌ No lo publiques en GitHub, Discord, foros ni chats.
✅ Si lo expones, revócalo inmediatamente desde https://my.telegram.org.
✅ Usa siempre .env y .gitignore para evitar fugas accidentales.
✅ Desactiva sesiones desconocidas desde la app de Telegram:
Ajustes → Privacidad y seguridad → Sesiones activas

🙌 Gracias por usar este componente
Este script simplifica la autenticación con Telegram para bots, automatizaciones, scrapers y más. Úsalo con responsabilidad y ética.
