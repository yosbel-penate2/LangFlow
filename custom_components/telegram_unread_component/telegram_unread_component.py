import asyncio
import os
import time
import nest_asyncio
from typing import Any, Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    FloodWaitError,
    RPCError
)
from telethon.sessions import StringSession

# Aplicar nest_asyncio para permitir loops anidados
nest_asyncio.apply()

# Importaciones de Langflow
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, Output, SecretStrInput, StrInput, BoolInput
from lfx.schema.data import Data
from lfx.log.logger import logger


class TelegramUnreadMessages(Component):
    display_name = "Telegram Unread Messages"
    description = "Fetches unread messages from one contact from Telegram using session string."
    icon = "message-circle"
    name = "TelegramUnreadMessages"

    inputs = [
        SecretStrInput(
            name="api_id",
            display_name="API ID",
            info="Your Telegram API ID from https://my.telegram.org",
            required=True,
        ),
        SecretStrInput(
            name="api_hash",
            display_name="API Hash",
            info="Your Telegram API Hash from https://my.telegram.org",
            required=True,
        ),
        SecretStrInput(
            name="session_string",
            display_name="Session String",
            info="PEGA AQUÍ TU SESSION_STRING (generado con el script)",
            required=True,
            placeholder="1aaNk8EX-YRfwoRsebUkugFvht6DUPi...",
        ),
        StrInput(
            name="chat_identifier",
            display_name="Chat Identifier",
            info="Chat username, phone number, or title",
            required=True,
            placeholder="@username or chat title",
        ),
        IntInput(
            name="limit",
            display_name="Message Limit",
            info="Maximum messages to fetch",
            value=50,
            required=True,
        ),
        IntInput(
            name="max_unread",
            display_name="Max Unread Output",
            info="Maximum unread messages to return",
            value=10,
            required=True,
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            info="Max time to wait for Telegram",
            value=30,
            required=True,
        ),
        BoolInput(
            name="mark_as_read",
            display_name="Mark as Read",
            info="Mark fetched messages as read",
            value=False,
        ),
    ]

    outputs = [
        Output(
            display_name="Unread Messages",
            name="unread_messages",
            method="fetch_unread_messages",
        ),
    ]

    def fetch_unread_messages(self) -> List[Data]:
        """
        Método principal con manejo CORRECTO de event loop.
        """
        start_time = time.time()

        # Validar session string
        if not self.session_string or len(self.session_string.strip()) < 10:
            self.status = "❌ Session string inválido o muy corto"
            return []

        # Crear un nuevo event loop para esta operación
        loop = None
        try:
            # Crear loop completamente nuevo
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Ejecutar la tarea con timeout
            messages = loop.run_until_complete(
                asyncio.wait_for(
                    self._fetch_unread_async(),
                    timeout=self.timeout_seconds
                )
            )

            # Crear objetos Data
            data_objects = []
            for msg_data in messages:
                data_obj = Data(
                    text=msg_data["text"],
                    data={
                        "message_id": msg_data["id"],
                        "date": msg_data["date"],
                        "sender_id": msg_data["sender_id"],
                        "chat_id": msg_data["chat_id"],
                        "chat_name": msg_data["chat_name"],
                    }
                )
                data_objects.append(data_obj)

            elapsed = time.time() - start_time
            self.status = f"✅ {len(data_objects)} mensajes en {elapsed:.1f}s"
            return data_objects

        except asyncio.TimeoutError:
            self.status = f"⏱️ Timeout después de {self.timeout_seconds}s"
            return []
        except Exception as e:
            error_msg = str(e)
            self.status = f"❌ Error: {error_msg}"
            logger.error(f"Telegram error: {error_msg}")
            return []
        finally:
            # IMPORTANTE: Limpiar el loop correctamente
            if loop and loop.is_running():
                loop.stop()
            if loop and not loop.is_closed():
                # Cancelar todas las tareas pendientes
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                # Cerrar el loop
                loop.close()

    async def _fetch_unread_async(self) -> List[Dict]:
        """
        Versión asíncrona con manejo robusto.
        """
        client = None

        try:
            # Limpiar el session string
            session_str = self.session_string.strip()

            # Crear StringSession
            try:
                session = StringSession(session_str)
                logger.info("📱 Usando StringSession")
            except Exception as e:
                logger.error(f"Error al crear StringSession: {e}")
                raise ValueError(f"Session string inválido: {e}")

            # Crear cliente
            client = TelegramClient(
                session=session,
                api_id=int(self.api_id),
                api_hash=self.api_hash,
                timeout=10,
                request_retries=2,
                connection_retries=2,
            )

            # Conectar
            try:
                await asyncio.wait_for(client.connect(), timeout=10)
            except asyncio.TimeoutError:
                raise TimeoutError("No se puede conectar a Telegram")

            # Verificar autorización
            if not await client.is_user_authorized():
                raise ValueError("Session string no autorizado - genera uno nuevo")

            # Obtener entidad del chat
            entity = await self._get_chat_entity(client)
            if not entity:
                raise ValueError(f"Chat '{self.chat_identifier}' no encontrado")

            # Obtener mensajes
            messages = await asyncio.wait_for(
                client.get_messages(entity, limit=self.limit),
                timeout=10
            )

            # Obtener diálogos para read_inbox_max_id
            dialogs = await asyncio.wait_for(
                client.get_dialogs(),
                timeout=10
            )

            # Encontrar diálogo correcto
            target_dialog = next(
                (d for d in dialogs if d.entity.id == entity.id),
                None
            )

            # Filtrar mensajes no leídos
            read_max_id = target_dialog.dialog.read_inbox_max_id if target_dialog else 0
            unread_messages = []

            for msg in messages:
                if (not msg.out and
                    msg.id > read_max_id and
                    msg.text and
                    msg.text.strip()):

                    unread_messages.append({
                        "id": msg.id,
                        "text": msg.text,
                        "date": msg.date.isoformat() if msg.date else None,
                        "sender_id": msg.sender_id,
                        "chat_id": entity.id,
                        "chat_name": self._get_chat_name(entity),
                    })

            # Marcar como leídos
            if self.mark_as_read and unread_messages and target_dialog:
                last_id = max(msg["id"] for msg in unread_messages)
                await client.send_read_acknowledge(entity, max_id=last_id)

            return unread_messages[:self.max_unread]

        except FloodWaitError as e:
            raise ValueError(f"Flood wait: {e.seconds}s")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            # Desconectar cliente
            if client:
                try:
                    await asyncio.wait_for(client.disconnect(), timeout=5)
                except:
                    pass

    async def _get_chat_entity(self, client):
        """Obtener entidad del chat"""
        identifier = self.chat_identifier.strip()
        if identifier.startswith('@'):
            identifier = identifier[1:]

        try:
            return await client.get_entity(identifier)
        except:
            # Buscar en diálogos
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                if dialog.name and dialog.name.lower() == identifier.lower():
                    return dialog.entity
        return None

    def _get_chat_name(self, entity):
        """Nombre legible del chat"""
        if hasattr(entity, 'title') and entity.title:
            return entity.title
        elif hasattr(entity, 'username') and entity.username:
            return f"@{entity.username}"
        elif hasattr(entity, 'first_name') and entity.first_name:
            return f"{entity.first_name} {getattr(entity, 'last_name', '')}".strip()
        return str(entity.id)