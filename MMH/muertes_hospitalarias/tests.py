import requests

def test_large_volume_query():
    url = "http://127.0.0.1:8000/api/pacientes/"  # URL de tu endpoint
    params = {
        "limit": 10000  # Parámetro que define la cantidad de resultados
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Consulta exitosa. Total de registros obtenidos: {len(data)}")
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la consulta: {e}")

# Ejecutar el script
test_large_volume_query()
