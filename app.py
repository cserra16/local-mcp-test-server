import httpx
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP con el nombre del servicio
# host="0.0.0.0" permite conexiones desde cualquier IP en la red local (necesario para iOS)
mcp = FastMCP(
    "Multi-City Weather Service",
    host="0.0.0.0",
    port=8000
)

# Diccionario de ciudades con sus coordenadas (latitud, longitud)
CITIES = {
    "lhospitalet": {
        "name": "L'Hospitalet de Llobregat",
        "latitude": 41.3597,
        "longitude": 2.1003,
        "timezone": "Europe/Madrid"
    },
    "barcelona": {
        "name": "Barcelona",
        "latitude": 41.3851,
        "longitude": 2.1734,
        "timezone": "Europe/Madrid"
    },
    "madrid": {
        "name": "Madrid",
        "latitude": 40.4168,
        "longitude": -3.7038,
        "timezone": "Europe/Madrid"
    },
    "valencia": {
        "name": "Valencia",
        "latitude": 39.4699,
        "longitude": -0.3763,
        "timezone": "Europe/Madrid"
    },
    "sevilla": {
        "name": "Sevilla",
        "latitude": 37.3886,
        "longitude": -5.9823,
        "timezone": "Europe/Madrid"
    },
    "bilbao": {
        "name": "Bilbao",
        "latitude": 43.2630,
        "longitude": -2.9350,
        "timezone": "Europe/Madrid"
    },
    "malaga": {
        "name": "Málaga",
        "latitude": 36.7213,
        "longitude": -4.4214,
        "timezone": "Europe/Madrid"
    },
    "zaragoza": {
        "name": "Zaragoza",
        "latitude": 41.6488,
        "longitude": -0.8891,
        "timezone": "Europe/Madrid"
    }
}

# Códigos meteorológicos WMO para descripción del cielo
WMO_CODES = {
    0: "Cielo despejado",
    1: "Principalmente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada intensa",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos intensos",
    95: "Tormenta",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo intenso",
}


def get_weather_description(code: int) -> str:
    """Convierte un código WMO a descripción legible."""
    return WMO_CODES.get(code, f"Código desconocido ({code})")


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    Obtiene el clima actual de una ciudad específica.
    Devuelve temperatura, humedad y descripción del estado del cielo.

    Args:
        city: Nombre de la ciudad (opciones disponibles: lhospitalet, barcelona,
              madrid, valencia, sevilla, bilbao, malaga, zaragoza)

    Returns:
        str: Información del clima incluyendo temperatura en grados Celsius,
             porcentaje de humedad relativa y estado del cielo.

    Examples:
        - "¿Qué tiempo hace en Barcelona?"
        - "Clima de Madrid"
        - "Temperatura en Valencia"
    """
    # Normalizar el nombre de la ciudad
    city_key = city.lower().strip()

    # Buscar la ciudad en el diccionario
    if city_key not in CITIES:
        available_cities = ", ".join([CITIES[k]["name"] for k in CITIES.keys()])
        return f"Ciudad '{city}' no encontrada. Ciudades disponibles: {available_cities}"

    city_data = CITIES[city_key]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city_data["latitude"],
        "longitude": city_data["longitude"],
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
        "timezone": city_data["timezone"]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            curr = data["current"]
            temp = curr["temperature_2m"]
            hum = curr["relative_humidity_2m"]
            weather_code = curr.get("weather_code", 0)
            sky_description = get_weather_description(weather_code)

            return (
                f"Clima en {city_data['name']}: {temp}°C, "
                f"Humedad: {hum}%, "
                f"Estado del cielo: {sky_description}. "
                f"Datos provistos por Open-Meteo."
            )
        except httpx.TimeoutException:
            return "Error: Tiempo de espera agotado al consultar la API meteorológica."
        except httpx.HTTPStatusError as e:
            return f"Error HTTP al consultar el clima: {e.response.status_code}"
        except Exception as e:
            return f"Error al consultar el clima: {str(e)}"


@mcp.tool()
async def get_weather_lhospitalet() -> str:
    """
    Obtiene el clima actual de L'Hospitalet de Llobregat (Barcelona).
    Devuelve temperatura, humedad y descripción del estado del cielo.

    Usa esta herramienta cuando el usuario pregunte por el tiempo o clima en:
    - L'Hospitalet de Llobregat
    - Hospitalet
    - Hospi
    - L'Hospi
    - L'H

    Esta herramienta consulta la API de Open-Meteo para obtener datos
    meteorológicos en tiempo real de la ciudad de L'Hospitalet de Llobregat,
    situada en el área metropolitana de Barcelona, España.

    Returns:
        str: Información del clima incluyendo temperatura en grados Celsius,
             porcentaje de humedad relativa y estado del cielo.
    """
    return await get_weather("lhospitalet")


def main():
    """Punto de entrada para ejecutar el servidor MCP con transporte SSE."""
    # Usar transporte 'sse' para permitir conexión desde iOS (red local)
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
