def entidades_con_mayor_tiempo_promedio_de_tiempo_de_cierre_de_incidentes():
    import pymongo
    from django.conf import settings
    import datetime
    import csv

    my_client = pymongo.MongoClient(settings.DB_NAME)
    dbname = my_client['dds2023']
    collection = dbname["incidente"]
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    pipeline = [
        {"$match": {"fechaCierre": {"$gte": one_week_ago},"solucionado": True}},
        {"$project": {"entidad": 1, "promedio_tiempo_cierre": {"$divide": [{ "$subtract": ["$fechaCierre", "$fechaCreado"] }, 3600000]}}},
        {"$group": {"_id": "$entidad", "promedio_tiempo_cierre": { "$avg": "$promedio_tiempo_cierre" }}},
        {"$sort": {"promedio_tiempo_cierre": -1}}
    ]

    establecimientos_ordenados = list(collection.aggregate(pipeline))

    timestamp_actual = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"./DDS/rankings/entidades-con-mayor-tiempo-de-cierre-{timestamp_actual}.csv"
    nombres_columnas = ["entidad", "tiempo_promedio_de_cierre"]

    with open(nombre_archivo, mode='x', newline='') as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=nombres_columnas)
        escritor_csv.writeheader()
        for establecimiento in establecimientos_ordenados:
            fila = {}
            fila['entidad'] = establecimiento['_id']
            fila['tiempo_promedio_de_cierre'] = establecimiento['promedio_tiempo_cierre']
            escritor_csv.writerow(fila)

    return

def entidades_con_mayor_incidentes_reportados_en_la_semana():
    import pymongo
    from django.conf import settings
    import datetime
    import csv

    my_client = pymongo.MongoClient(settings.DB_NAME)
    dbname = my_client['dds2023']
    collection = dbname["incidente"]
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    pipeline = [
        {"$match": {"fechaCreado": {"$gte": one_week_ago}}}
    ]

    incidentes = list(collection.aggregate(pipeline))

    incidentes_ordenados = sorted(incidentes, key=lambda x: x['fechaCierre'])

    incidentes_repetidos = {}
    conteo_incidentes = {}
    for incidente in incidentes_ordenados:
        if incidente['servicio'] not in incidentes_repetidos:
            if incidente['solucionado']:
                incidentes_repetidos[incidente['servicio']] = min(incidente['fechaCierre'], incidente['fechaCreado']+datetime.timedelta(days=1))
                if incidente['entidad'] in conteo_incidentes:
                    conteo_incidentes[incidente['entidad']] += 1
                else:
                    conteo_incidentes[incidente['entidad']] = 1
            else:
                incidentes_repetidos[incidente['servicio']] = incidente['fechaCreado']+datetime.timedelta(days=1)
                if incidente['entidad'] in conteo_incidentes:
                    conteo_incidentes[incidente['entidad']] += 1
                else:
                    conteo_incidentes[incidente['entidad']] = 1
        else:
            i = incidentes_repetidos[incidente['servicio']]
            if incidente['fechaCreado'] < i:
                continue
            else:
                if incidente['solucionado']:
                    incidentes_repetidos[incidente['servicio']] = min(incidente['fechaCierre'], incidente['fechaCreado']+datetime.timedelta(days=1))
                    if incidente['entidad'] in conteo_incidentes:
                        conteo_incidentes[incidente['entidad']] += 1
                    else:
                        conteo_incidentes[incidente['entidad']] = 1
                else:
                    incidentes_repetidos[incidente['servicio']] = incidente['fechaCreado']+datetime.timedelta(days=1)
                    if incidente['entidad'] in conteo_incidentes:
                        conteo_incidentes[incidente['entidad']] += 1
                    else:
                        conteo_incidentes[incidente['entidad']] = 1

    timestamp_actual = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo = f"./DDS/rankings/entidades-con-mas-incidentes-{timestamp_actual}.csv"
    nombres_columnas = ["entidad", "cant_incidentes"]

    with open(nombre_archivo, mode='x', newline='') as archivo_csv:
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=nombres_columnas)
        escritor_csv.writeheader()
        for conteo in conteo_incidentes:
            fila = {}
            fila['entidad'] = conteo
            fila['cant_incidentes'] = conteo_incidentes[conteo]
            escritor_csv.writerow(fila)

    return