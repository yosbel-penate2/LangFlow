import asyncio
import time
from typing import Any, Optional, List, Dict
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
import nest_asyncio

# Aplicar nest_asyncio
nest_asyncio.apply()

# Importaciones de Langflow
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, Output, SecretStrInput, StrInput, BoolInput
from lfx.schema.data import Data
from lfx.log.logger import logger


class TelegramMultiChatReader(Component):
    display_name = "Telegram Multi-Chat Reader"
    description = "Lee mensajes no leídos de múltiples chats de Telegram"
    icon = "message-circle"
    name = "TelegramMultiChatReader"

    inputs = [
        SecretStrInput(
            name="api_id",
            display_name="API ID",
            info="Tu API ID de https://my.telegram.org",
            required=True,
        ),
        SecretStrInput(
            name="api_hash",
            display_name="API Hash",
            info="Tu API Hash de https://my.telegram.org",
            required=True,
        ),
        SecretStrInput(
            name="session_string",
            display_name="Session String",
            info="Session string generada con Telethon",
            required=True,
        ),
        StrInput(
            name="chats_input",
            display_name="Chats",
            info="Lista de chats separados por comas (ej: @canal1, Mi Grupo, +521234567890)",
            required=True,
            value="@canal_pruebas",
        ),
        IntInput(
            name="limit_per_chat",
            display_name="Messages per chat",
            info="Máximo de mensajes a obtener por chat",
            value=50,
        ),
        IntInput(
            name="max_unread_per_chat",
            display_name="Max unread per chat",
            info="Máximo de mensajes no leídos a devolver por chat",
            value=10,
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            info="Tiempo máximo de espera",
            value=30,
        ),
        BoolInput(
            name="mark_as_read",
            display_name="Mark as read",
            info="Marcar mensajes como leídos",
            value=False,
        ),
        BoolInput(
            name="include_read",
            display_name="Include read messages",
            info="Incluir mensajes ya leídos (para pruebas)",
            value=False,
        ),
    ]

    outputs = [
        Output(
            display_name="All Messages",
            name="all_messages",
            method="get_all_messages",
        ),
        Output(
            display_name="Messages by Chat",
            name="messages_by_chat",
            method="get_messages_by_chat",
        ),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_results = []

    def _parse_chats(self) -> List[str]:
        """Convierte la entrada de chats en lista"""
        if not self.chats_input:
            return []
        # Separar por comas y limpiar espacios
        chats = [c.strip() for c in self.chats_input.split(',') if c.strip()]
        return chats

    def get_all_messages(self) -> List[Data]:
        """Obtiene todos los mensajes de todos los chats"""
        start_time = time.time()
        all_messages = []

        # Validar session string
        if not self.session_string or len(self.session_string.strip()) < 10:
            self.status = "❌ Session string inválido"
            return []

        # Parsear chats
        chats = self._parse_chats()
        if not chats:
            self.status = "❌ No hay chats configurados"
            return []

        # Crear event loop
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Procesar cada chat
            for chat_identifier in chats:
                try:
                    messages = loop.run_until_complete(
                        asyncio.wait_for(
                            self._fetch_chat_messages(chat_identifier),
                            timeout=self.timeout_seconds
                        )
                    )
                    all_messages.extend(messages)
                except asyncio.TimeoutError:
                    logger.error(f"Timeout en chat {chat_identifier}")
                except Exception as e:
                    logger.error(f"Error en chat {chat_identifier}: {e}")

            # Guardar resultados
            self._last_results = all_messages

            elapsed = time.time() - start_time
            self.status = f"✅ {len(all_messages)} mensajes de {len(chats)} chats en {elapsed:.1f}s"
            return all_messages

        except Exception as e:
            self.status = f"❌ Error: {str(e)}"
            logger.error(f"Error general: {e}")
            return []
        finally:
            if loop:
                if loop.is_running():
                    loop.stop()
                if not loop.is_closed():
                    loop.close()

    async def _fetch_chat_messages(self, chat_identifier: str) -> List[Data]:
        """Obtiene mensajes de un chat específico"""
        client = None

        try:
            # Limpiar identifier
            identifier = chat_identifier.strip()

            # Crear cliente
            session = StringSession(self.session_string.strip())
            client = TelegramClient(
                session=session,
                api_id=int(self.api_id),
                api_hash=self.api_hash,
                timeout=10,
            )

            # Conectar
            await client.connect()

            # Verificar autorización
            if not await client.is_user_authorized():
                raise ValueError("Session string no autorizado")

            # Obtener entidad del chat
            entity = await self._get_chat_entity(client, identifier)
            if not entity:
                logger.warning(f"Chat no encontrado: {identifier}")
                return []

            # Obtener mensajes
            messages = await client.get_messages(entity, limit=self.limit_per_chat)

            # Si no queremos incluir leídos, necesitamos el read_max_id
            read_max_id = 0
            if not self.include_read:
                try:
                    dialogs = await client.get_dialogs()
                    target_dialog = next(
                        (d for d in dialogs if d.entity.id == entity.id),
                        None
                    )
                    if target_dialog:
                        read_max_id = target_dialog.dialog.read_inbox_max_id or 0
                except:
                    pass

            # Procesar mensajes
            result = []
            chat_name = self._get_chat_name(entity)

            for msg in messages:
                # Determinar si es no leído (si aplica)
                is_unread = self.include_read or (not msg.out and msg.id > read_max_id)

                # Si estamos incluyendo leídos O es no leído
                if self.include_read or is_unread:
                    # Solo mensajes con texto
                    if msg.text and msg.text.strip():
                        data_obj = Data(
                            text=msg.text,
                            data={
                                "message_id": msg.id,
                                "date": msg.date.isoformat() if msg.date else None,
                                "sender_id": msg.sender_id,
                                "chat_id": entity.id,
                                "chat_name": chat_name,
                                "chat_identifier": identifier,
                                "is_unread": is_unread,
                                "outgoing": msg.out,
                            }
                        )
                        result.append(data_obj)

                        # Limitar por max_unread_per_chat si aplica
                        if not self.include_read and len(result) >= self.max_unread_per_chat:
                            break

            # Marcar como leídos si es necesario
            if self.mark_as_read and result and not self.include_read:
                try:
                    last_id = max(d.data["message_id"] for d in result)
                    await client.send_read_acknowledge(entity, max_id=last_id)
                except:
                    pass

            return result

        except FloodWaitError as e:
            logger.warning(f"Flood wait en {chat_identifier}: {e.seconds}s")
            return []
        except Exception as e:
            logger.error(f"Error en chat {chat_identifier}: {e}")
            return []
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass

    async def _get_chat_entity(self, client, identifier: str):
        """Obtiene la entidad del chat"""
        # Limpiar @ si existe
        clean_id = identifier.strip()
        if clean_id.startswith('@'):
            clean_id = clean_id[1:]

        # Intentar get_entity
        try:
            return await client.get_entity(clean_id)
        except:
            pass

        # Buscar en diálogos
        try:
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                # Comparar por nombre
                if dialog.name and dialog.name.lower() == clean_id.lower():
                    return dialog.entity
                # Comparar por username
                if hasattr(dialog.entity, 'username') and dialog.entity.username:
                    if dialog.entity.username.lower() == clean_id.lower():
                        return dialog.entity
        except:
            pass

        return None

    def _get_chat_name(self, entity):
        """Nombre legible del chat"""
        if hasattr(entity, 'title') and entity.title:
            return entity.title
        elif hasattr(entity, 'username') and entity.username:
            return f"@{entity.username}"
        elif hasattr(entity, 'first_name') and entity.first_name:
            last = getattr(entity, 'last_name', '')
            return f"{entity.first_name} {last}".strip()
        return str(entity.id)

    def get_messages_by_chat(self) -> Dict[str, List[Data]]:
        """Agrupa mensajes por chat"""
        # Si ya tenemos resultados, usarlos
        if self._last_results:
            messages = self._last_results
        else:
            # Si no, obtenerlos
            messages = self.get_all_messages()

        # Agrupar por chat_name
        result = {}
        for msg in messages:
            chat_name = msg.data.get("chat_name", "unknown")
            if chat_name not in result:
                result[chat_name] = []
            result[chat_name].append(msg)

        return result