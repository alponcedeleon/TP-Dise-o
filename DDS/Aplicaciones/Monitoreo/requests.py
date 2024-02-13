import requests

def obtener_ubicacion(latitud, longitud):
    try:
        url = 'https://apis.datos.gob.ar/georef/api/ubicacion'
        parametros = {
            'lat': latitud,
            'lon': longitud,
        }

        response = requests.get(url, params=parametros)

        if response.status_code == 200:
            datos_json = response.json()
            return datos_json['ubicacion']
        else:
            print(f"Error al obtener datos: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de solicitud: {e}")
        return None
    
def obtener_localidades():
    try:
        url = 'https://apis.datos.gob.ar/georef/api/localidades'
        parametros = {
            'provincia': 'Ciudad Autónoma de Buenos Aires',
            'campos': 'nombre',
            'max':'1000'
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

def obtener_provincias():
    try:
        url = 'https://apis.datos.gob.ar/georef/api/provincias'
        parametros = {
            'campos': 'nombre',
            'max':'1000'
        }

        response = requests.get(url, params=parametros)

        if response.status_code == 200:
            datos_json = response.json()
            return datos_json['provincias']
        else:
            print(f"Error al obtener datos: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error de solicitud: {e}")
        return None
