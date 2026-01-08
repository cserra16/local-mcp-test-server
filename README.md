# Local MCP Test Server

Servidor MCP (Model Context Protocol) de pruebas locales que expone herramientas meteorológicas para múltiples ciudades mediante transporte SSE, compatible con dispositivos móviles (iOS/Android).

## Características

- **Transporte SSE** para conexión desde apps móviles en red local
- **API Open-Meteo** (gratuita, sin API key)
- **FastMCP** para registro automático de herramientas
- **Compatible con Qwen 2.5** y otros LLMs

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.11+ |
| Framework MCP | mcp[cli] + FastMCP |
| Cliente HTTP | httpx (async) |
| Servidor ASGI | uvicorn + starlette |

## Requisitos

- Python 3.11+
- pip o uv

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/cserra16/local-mcp-test-server.git
cd local-mcp-test-server

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
source venv/bin/activate
python app.py
```

El servidor iniciará en `http://0.0.0.0:8000` con transporte SSE.

## Endpoints MCP

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/sse` | Handshake SSE (obtiene session_id) |
| POST | `/messages/?session_id=...` | Mensajes JSON-RPC |

## Herramientas Disponibles

### `get_weather`

Obtiene el clima actual de una ciudad específica (generalizada).

**Parámetros:**
- `city` (string): Nombre de la ciudad

**Ciudades disponibles:**
- `lhospitalet` - L'Hospitalet de Llobregat
- `barcelona` - Barcelona
- `madrid` - Madrid
- `valencia` - Valencia
- `sevilla` - Sevilla
- `bilbao` - Bilbao
- `malaga` - Málaga
- `zaragoza` - Zaragoza

**Retorna:** Temperatura (°C), humedad relativa (%) y estado del cielo.

**Ejemplos de uso:**
- "¿Qué tiempo hace en Barcelona?"
- "Clima de Madrid"
- "Temperatura en Valencia"

**Ejemplo de respuesta:**
```
Clima en Barcelona: 18.5°C, Humedad: 65%, Estado del cielo: Parcialmente nublado. Datos provistos por Open-Meteo.
```

### `get_weather_lhospitalet`

Obtiene el clima actual de L'Hospitalet de Llobregat (Barcelona). Esta herramienta es un wrapper de compatibilidad que utiliza internamente `get_weather`.

**Triggers:** El LLM invocará esta herramienta cuando el usuario pregunte por el clima en:
- L'Hospitalet de Llobregat
- Hospitalet
- Hospi
- L'Hospi
- L'H

**Retorna:** Temperatura (°C), humedad relativa (%) y estado del cielo.

**Ejemplo de respuesta:**
```
Clima en L'Hospitalet de Llobregat: 18.5°C, Humedad: 65%, Estado del cielo: Parcialmente nublado. Datos provistos por Open-Meteo.
```

## Pruebas

### Con MCP Inspector (recomendado)

```bash
npx -y @modelcontextprotocol/inspector http://localhost:8000/sse
```

### Test con Python

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    async with sse_client('http://localhost:8000/sse') as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ejemplo 1: Consultar clima de Barcelona
            result = await session.call_tool('get_weather', {'city': 'barcelona'})
            print(result.content[0].text)

            # Ejemplo 2: Consultar clima de Madrid
            result = await session.call_tool('get_weather', {'city': 'madrid'})
            print(result.content[0].text)

            # Ejemplo 3: Usando la herramienta legacy
            result = await session.call_tool('get_weather_lhospitalet', {})
            print(result.content[0].text)

asyncio.run(test())
```

### Desde el navegador

Acceder a `http://localhost:8000/sse` para verificar eventos SSE.

## Conexión desde iOS

1. Asegúrate de que el iPhone esté en la misma red Wi-Fi
2. Obtén la IP local: `ipconfig getifaddr en0`
3. Conecta desde la app iOS a `http://<IP-LOCAL>:8000/sse`

## Estructura del Proyecto

```
local-mcp-test-server/
├── app.py              # Servidor MCP principal
├── requirements.txt    # Dependencias
├── pyproject.toml      # Configuración del proyecto
└── README.md
```

## Licencia

MIT