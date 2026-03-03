import asyncio
import time
from typing import Any, Optional, List, Dict
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession
import nest_asyncio
from langflow.schema import DataFrame  # ✅ Usar el DataFrame de langflow.schema
import pandas as pd


# Aplicar nest_asyncio
nest_asyncio.apply()

# Importaciones de Langflow
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, Output, SecretStrInput, StrInput, BoolInput, MultilineInput
from lfx.schema.data import Data
from lfx.log.logger import logger


class TelegramMultiChatReader(Component):
    display_name = "Telegram Multi-Chat Reader"
    description = "Lee mensajes no leídos de múltiples chats de Telegram (optimizado)"
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
        MultilineInput(
            name="chats_input",
            display_name="Chats",
            info="Lista de chats (uno por línea o separados por comas)",
            required=True,
            value="@canal_pruebas\nMi Grupo\n+521234567890",
        ),
        IntInput(
            name="limit_per_chat",
            display_name="Messages per chat",
            info="Máximo de mensajes a obtener por chat",
            value=20,  # Reducido para mayor velocidad
        ),
        IntInput(
            name="max_unread_per_chat",
            display_name="Max unread per chat",
            info="Máximo de mensajes no leídos a devolver por chat",
            value=5,  # Reducido para mayor velocidad
        ),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (seconds)",
            info="Tiempo máximo de espera",
            value=15,  # Reducido para timeout más rápido
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
        BoolInput(
            name="parallel_mode",
            display_name="Parallel mode",
            info="Consultar chats en paralelo (más rápido pero más uso de memoria)",
            value=True,
        ),
        IntInput(
            name="max_parallel",
            display_name="Max parallel chats",
            info="Máximo de chats a consultar simultáneamente",
            value=3,
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
        self._client_cache = {}  # Caché simple de clientes

    def _parse_chats(self) -> List[str]:
        """Convierte la entrada de chats en lista"""
        if not self.chats_input:
            return []

        lines = self.chats_input.split('\n')
        chats = []

        for line in lines:
            if ',' in line:
                for item in line.split(','):
                    item = item.strip()
                    if item:
                        chats.append(item)
            else:
                line = line.strip()
                if line:
                    chats.append(line)

        return chats

    async def _get_cached_client(self):
        """Obtiene o crea un cliente con caché simple"""
        cache_key = f"{self.api_id}:{self.session_string[-10:]}"

        if cache_key in self._client_cache:
            client = self._client_cache[cache_key]
            # Verificar si sigue conectado
            if client.is_connected():
                return client
            else:
                # Intentar reconectar
                try:
                    await client.connect()
                    return client
                except:
                    del self._client_cache[cache_key]

        # Crear nuevo cliente
        session = StringSession(self.session_string.strip())
        client = TelegramClient(
            session=session,
            api_id=int(self.api_id),
            api_hash=self.api_hash,
            timeout=5,  # Timeout reducido
            connection_retries=1,  # Menos reintentos
        )

        await client.connect()

        if not await client.is_user_authorized():
            raise ValueError("Session string no autorizado")

        # Guardar en caché
        self._client_cache[cache_key] = client
        return client

    async def _fetch_chat_messages(self, chat_identifier: str) -> List[Data]:
        """Obtiene mensajes de un chat específico - VERSIÓN OPTIMIZADA"""
        try:
            identifier = chat_identifier.strip()

            # Obtener cliente (con caché)
            client = await self._get_cached_client()

            # Obtener entidad del chat (con caché implícito de Telethon)
            entity = await self._get_chat_entity(client, identifier)
            if not entity:
                logger.warning(f"Chat no encontrado: {identifier}")
                return []

            # Obtener SOLO mensajes no leídos si es posible
            if not self.include_read:
                # Intentar obtener primero el read_max_id para limitar la consulta
                try:
                    dialogs = await client.get_dialogs()
                    target_dialog = next(
                        (d for d in dialogs if d.entity.id == entity.id),
                        None
                    )
                    if target_dialog:
                        read_max_id = target_dialog.dialog.read_inbox_max_id or 0
                        # Obtener mensajes DESPUÉS del último leído (más eficiente)
                        messages = await client.get_messages(
                            entity,
                            limit=self.limit_per_chat,
                            min_id=read_max_id  # Solo mensajes más nuevos que el último leído
                        )
                    else:
                        messages = await client.get_messages(entity, limit=self.limit_per_chat)
                        read_max_id = 0
                except:
                    messages = await client.get_messages(entity, limit=self.limit_per_chat)
                    read_max_id = 0
            else:
                messages = await client.get_messages(entity, limit=self.limit_per_chat)
                read_max_id = 0

            # Procesar mensajes (solo metadata, no texto completo si no es necesario)
            result = []
            chat_name = self._get_chat_name(entity)
            count = 0

            for msg in messages:
                # Para no leídos, filtrar rápidamente
                if not self.include_read:
                    if msg.out or msg.id <= read_max_id:
                        continue

                # Solo texto no vacío
                if not msg.text or not msg.text.strip():
                    continue

                # Crear Data object con texto truncado para mayor velocidad
                text = msg.text[:1000] if len(msg.text) > 1000 else msg.text

                data_obj = Data(
                    text=text,
                    data={
                        "message_id": msg.id,
                        "date": msg.date.isoformat() if msg.date else None,
                        "sender_id": msg.sender_id,
                        "chat_id": entity.id,
                        "chat_name": chat_name,
                        "chat_identifier": identifier,
                        "is_unread": not self.include_read and not msg.out and msg.id > read_max_id,
                        "outgoing": msg.out,
                    }
                )
                result.append(data_obj)
                count += 1

                # Límite rápido
                if not self.include_read and count >= self.max_unread_per_chat:
                    break

            # Marcar como leídos si es necesario (solo si hay mensajes nuevos)
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

    async def _fetch_chat_messages_parallel(self, chat_identifiers: List[str]) -> List[Data]:
        """Obtiene mensajes de múltiples chats en paralelo"""
        if not self.parallel_mode or len(chat_identifiers) == 1:
            # Modo secuencial
            all_messages = []
            for chat_id in chat_identifiers:
                messages = await self._fetch_chat_messages(chat_id)
                all_messages.extend(messages)
            return all_messages

        # Modo paralelo con semáforo para limitar concurrencia
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def fetch_with_semaphore(chat_id):
            async with semaphore:
                return await self._fetch_chat_messages(chat_id)

        # Ejecutar todas las consultas en paralelo
        tasks = [fetch_with_semaphore(chat_id) for chat_id in chat_identifiers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combinar resultados
        all_messages = []
        for r in results:
            if isinstance(r, list):
                all_messages.extend(r)
            elif isinstance(r, Exception):
                logger.error(f"Error en consulta paralela: {r}")

        return all_messages

    def get_all_messages(self) -> List[Data]:
        """Obtiene todos los mensajes de todos los chats - VERSIÓN OPTIMIZADA"""
        start_time = time.time()

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

            # Ejecutar consultas (secuencial o paralelo)
            messages = loop.run_until_complete(
                asyncio.wait_for(
                    self._fetch_chat_messages_parallel(chats),
                    timeout=self.timeout_seconds
                )
            )

            # Guardar resultados
            self._last_results = messages

            elapsed = time.time() - start_time
            self.status = f"✅ {len(messages)} mensajes de {len(chats)} chats en {elapsed:.1f}s"
            return messages

        except asyncio.TimeoutError:
            self.status = f"⏱️ Timeout después de {self.timeout_seconds}s"
            return []
        except Exception as e:
            self.status = f"❌ Error: {str(e)}"
            logger.error(f"Error general: {e}")
            return []
        finally:
            # No cerramos los clientes aquí para mantener el caché
            if loop:
                if loop.is_running():
                    loop.stop()
                if not loop.is_closed():
                    loop.close()

    async def _get_chat_entity(self, client, identifier: str):
        """Obtiene la entidad del chat"""
        clean_id = identifier.strip()
        if clean_id.startswith('@'):
            clean_id = clean_id[1:]

        # Intentar get_entity (Telethon tiene su propio caché)
        try:
            return await client.get_entity(clean_id)
        except:
            pass

        # Buscar en diálogos (solo como fallback)
        try:
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                if dialog.name and dialog.name.lower() == clean_id.lower():
                    return dialog.entity
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

    def get_messages_by_chat(self) -> DataFrame:
        """Agrupa mensajes por chat y devuelve un DataFrame compatible con Langflow (langflow.schema.DataFrame)"""
        if self._last_results:
            messages = self._last_results
        else:
            messages = self.get_all_messages()

        # Convertir lista de objetos Data a filas
        rows = []
        for msg in messages:
            row = {
                "chat_name": msg.data.get("chat_name", "unknown"),
                "message_id": msg.data.get("message_id"),
                "date": msg.data.get("date"),
                "sender_id": msg.data.get("sender_id"),
                "chat_id": msg.data.get("chat_id"),
                "chat_identifier": msg.data.get("chat_identifier"),
                "is_unread": msg.data.get("is_unread"),
                "outgoing": msg.data.get("outgoing"),
                "text": msg.text
            }
            rows.append(row)

        # Crear DataFrame de pandas
        pd_df = pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=[
                "chat_name", "message_id", "date", "sender_id",
                "chat_id", "chat_identifier", "is_unread", "outgoing", "text"
            ]
        )

        # ✅ Devolver como langflow.schema.DataFrame (wrapper correcto para Langflow)
        return DataFrame(pd_df)