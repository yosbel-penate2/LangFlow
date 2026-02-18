from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

# Tus credenciales de https://my.telegram.org
API_ID = os.getenv('API_ID')  # Reemplaza con tu API ID (número)
API_HASH = os.getenv('API_HASH')  # Reemplaza con tu API Hash

if not API_ID or not API_HASH:
    raise ValueError("❌ Faltan API_ID o API_HASH en el archivo .env")

# Convertir API_ID a entero
try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("❌ API_ID debe ser un número entero")

print("=== GENERADOR DE STRING SESSION PARA TELEGRAM ===")
print("1. Te pedirá tu número de teléfono")
print("2. Recibirás un código SMS")
print("3. Al finalizar, obtendrás tu session_string")
print("=" * 50)

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    # Esto iniciará el proceso interactivo
    client.start()
    
    # Obtener el session_string
    session_string = client.session.save()
    
    print("\n" + "=" * 50)
    print("✅ ¡SESIÓN GENERADA CON ÉXITO!")
    print("\n🔐 TU STRING SESSION (GUÁRDALO SEGURO):")
    print("-" * 50)
    print(session_string)
    print("-" * 50)
    print("\n📌 También se ha enviado a tus Mensajes Guardados de Telegram")
    print("⚠️  NUNCA compartas este string con nadie")