from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Tus credenciales de https://my.telegram.org
API_ID = 3670950  # Reemplaza con tu API ID (número)
API_HASH = '7b8e672da86cf2d4d05c63ddfdbc1a66'  # Reemplaza con tu API Hash

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