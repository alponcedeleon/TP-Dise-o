import requests


def obtener_localidades():
    try:
        url = 'https://apis.datos.gob.ar/georef/api/localidades'
        parametros = {
            'provincia': 'Ciudad Autónoma de Buenos Aires',
            'campos': 'nombre',
        }

        response = requests.get(url, params=parametros)

        if response.status_code == 200:
            datos_json = response.json()
            return datos_json['localidades']
        else:
            print(f"Error al obtener datos: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de solicitud: {e}")
        return None
