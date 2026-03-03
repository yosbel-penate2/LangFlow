---

# 🌐 Componentes para LangFlow

Este repositorio contiene componentes personalizados para [LangFlow](https://langflow.org) que extienden su funcionalidad para trabajar con Telegram y GigaChat.

---

## 📋 Tabla de Contenidos
- [Componente Telegram Multi-Chat Reader](#-telegram-multi-chat-reader-component)
- [Componente GigaChat Model](#-gigachat-model-component)
- [Instalación General](#-instalación-general)
- [Seguridad](#-seguridad)

---

## 🇪🇸 Español

### 📱 Componente Telegram Multi-Chat Reader

**Telegram Multi-Chat Reader** es un componente personalizado para LangFlow que permite leer mensajes de múltiples chats de Telegram en paralelo utilizando [Telethon](https://docs.telethon.dev/). Utiliza autenticación por sesión mediante `session_string` y genera datos como `langflow.schema.DataFrame` para una integración perfecta con otros componentes.

#### ✨ Características

- 🔐 Login seguro con `session_string` de Telethon
- 📥 Lectura simultánea de múltiples chats
- ⚡ Obtención paralela de mensajes (rendimiento optimizado)
- 📊 Salida como `langflow.schema.DataFrame`
- 🧩 Compatible con componentes `Parser`, `Prompt` y cadenas LLM

### 🤖 Componente GigaChat Model

Este componente permite utilizar los modelos de lenguaje avanzados de **GigaChat** (Sber) directamente en LangFlow.

#### ✨ Características

- ✅ Múltiples modelos: `GigaChat`, `GigaChat-Pro`, `GigaChat-Max`
- 🔐 Autenticación segura mediante credenciales API
- ⚙️ Configuración avanzada: temperatura, tokens máximos
- 🌍 Ideal para aplicaciones en ruso e inglés

---

## 🇬🇧 English

### 📱 Telegram Multi-Chat Reader Component

**Telegram Multi-Chat Reader** is a custom component for [LangFlow](https://langflow.org) that allows you to read messages from multiple Telegram chats in parallel using [Telethon](https://docs.telethon.dev/). It supports session authentication via `session_string` and outputs data as `langflow.schema.DataFrame` for seamless integration with downstream components.

#### ✨ Features

- 🔐 Secure login using Telethon `session_string`
- 📥 Read messages from multiple chats simultaneously
- ⚡ Parallel message fetching (optimized performance)
- 📊 Output as `langflow.schema.DataFrame`
- 🧩 Plug-and-play with `Parser`, `Prompt`, and LLM chains

### 🤖 GigaChat Model Component

This component enables using **GigaChat** (Sber's advanced language models) directly within LangFlow.

#### ✨ Features

- ✅ Multiple models: `GigaChat`, `GigaChat-Pro`, `GigaChat-Max`
- 🔐 Secure authentication via API credentials
- ⚙️ Advanced configuration: temperature, max tokens
- 🌍 Ideal for Russian and English language applications

---

## 🇷🇺 Русский

### 📱 Компонент Telegram Multi-Chat Reader

**Telegram Multi-Chat Reader** — это пользовательский компонент для [LangFlow](https://langflow.org), который позволяет читать сообщения из нескольких чатов Telegram параллельно с использованием [Telethon](https://docs.telethon.dev/). Поддерживает аутентификацию через `session_string` и выводит данные в формате `langflow.schema.DataFrame`.

#### ✨ Возможности

- 🔐 Безопасный вход с `session_string` Telethon
- 📥 Чтение сообщений из нескольких чатов одновременно
- ⚡ Параллельное получение сообщений
- 📊 Вывод в формате `langflow.schema.DataFrame`
- 🧩 Совместимость с компонентами `Parser`, `Prompt` и LLM

### 🤖 Компонент GigaChat Model

Компонент для использования передовых языковых моделей **GigaChat** от Сбера непосредственно в LangFlow.

#### ✨ Возможности

- ✅ Несколько моделей: `GigaChat`, `GigaChat-Pro`, `GigaChat-Max`
- 🔐 Безопасная аутентификация через API
- ⚙️ Гибкая настройка: температура, максимальное количество токенов
- 🌍 Подходит для задач на русском и английском языках

---

## 🛠 Instalación General

### Requisitos Previos / Prerequisites / Предварительные требования

- Python 3.8+
- LangFlow instalado
- Cuenta en Telegram y [my.telegram.org](https://my.telegram.org) (para componente Telegram)
- Cuenta en [GigaChat API](https://developers.sber.ru/) (para componente GigaChat)

### Instalación / Installation / Установка

1. **Clonar el repositorio / Clone the repository / Клонируйте репозиторий**

```bash
git clone https://github.com/tu-usuario/langflow-components.git
cd langflow-components
```

2. **Crear entorno virtual / Create virtual environment / Создайте виртуальное окружение**

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

3. **Instalar dependencias / Install dependencies / Установите зависимости**

```bash
pip install telethon python-dotenv pandas langflow
```

4. **Configurar variables de entorno / Set up environment variables / Настройте переменные окружения**

Crea un archivo `.env` en la raíz:
```env
# Para Telegram Component
API_ID=tu_api_id
API_HASH=tu_api_hash

# Para GigaChat Component
GIGACHAT_CREDENTIALS=tus_credenciales
```

---

## 🔐 Generar Session String (Solo Telegram)

### Español
La `session_string` autentica tu cliente sin necesidad de login repetido.

1. Ejecuta el generador:
```bash
python generate_session_string.py
```

2. Sigue las instrucciones e ingresa tu número de teléfono
3. Guarda el string generado de forma segura

### English
The `session_string` authenticates your client without repeated logins.

1. Run the generator:
```bash
python generate_session_string.py
```

2. Follow instructions and enter your phone number
3. Store the generated string securely

### Русский
`session_string` аутентифицирует клиент без повторных входов.

1. Запустите генератор:
```bash
python generate_session_string.py
```

2. Следуйте инструкциям и введите номер телефона
3. Сохраните сгенерированную строку в безопасном месте

---

## 🔧 Uso en LangFlow / Using in LangFlow / Использование в LangFlow

### Configurar ruta de componentes / Set components path / Установите путь к компонентам

```bash
# Windows
set LANGFLOW_COMPONENTS_PATH=ruta\a\tus\componentes

# macOS/Linux
export LANGFLOW_COMPONENTS_PATH=/ruta/a/tus/componentes
```

### Verificar instalación / Verify installation / Проверка установки

```bash
langflow run --log-level debug
```

---

## ⚠️ Seguridad / Security / Безопасность

| ❌ NO COMPARTAS / DO NOT SHARE / НЕ ДЕЛИТЕСЬ | ✅ RECOMENDACIONES / RECOMMENDATIONS / РЕКОМЕНДАЦИИ |
|----------------------------------------------|----------------------------------------------------|
| `session_string` de Telegram | Revocar sesiones expuestas en [my.telegram.org](https://my.telegram.org) |
| Credenciales de GigaChat | Monitorear sesiones activas en Telegram |
| API_ID y API_HASH | Usar `.gitignore` para proteger `.env` |
| Tokens de acceso | Rotar credenciales periódicamente |

---

## 🙌 Contribuciones / Contributing / Вклад

¿Encontraste un error? ¿Sugerencias? Abre un issue o envía un PR.

Encontrou um erro? Sugestões? Abra uma issue ou envie um PR.

Нашли ошибку? Есть предложения? Откройте issue или отправьте PR.

---

## 📄 Licencia / License / Лицензия

MIT © 2024

---

## 🆘 Soporte / Support / Поддержка

- 📚 [Documentación de LangFlow](https://docs.langflow.org)
- 📚 [Documentación de Telethon](https://docs.telethon.dev)
- 📚 [Documentación de GigaChat](https://developers.sber.ru/docs/ru/gigachat/api/overview)