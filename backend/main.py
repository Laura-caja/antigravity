# backend/main.py - Versión para Barrios Unidos
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import json
import os
import random
from math import radians, cos, sin, sqrt, pi


app = FastAPI()


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("=" * 60)
print("CARGANDO DATOS DE BARRIOS UNIDOS")
print("=" * 60)


# Rutas de los archivos
RUTA_DATOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datos")
RUTA_LOCALIDAD = os.path.join(RUTA_DATOS, "GeoJSON.json")
RUTA_ESTACIONES = os.path.join(RUTA_DATOS, "paradero_zonal.geojson")


# Variable global para almacenar los datos
localidad_data = None
estaciones_data = None
gdf_localidad = None
gdf_estaciones = None
puntos_interes = []


# Cargar localidad (Barrios Unidos)
try:
    if os.path.exists(RUTA_LOCALIDAD):
        gdf_localidad = gpd.read_file(RUTA_LOCALIDAD)
        localidad_data = json.loads(gdf_localidad.to_json())
        print(f"✅ Localidad cargada: {RUTA_LOCALIDAD}")
        print(f"   Número de polígonos: {len(gdf_localidad)}")
        print(f"   Columnas: {list(gdf_localidad.columns)}")
       
        # Verificar si tiene nombre
        if 'nombre' in gdf_localidad.columns:
            nombres = gdf_localidad['nombre'].unique()
            print(f"   Nombres en archivo: {nombres}")
        else:
            print("   ⚠️ El archivo no tiene columna 'nombre'")
            # Agregar nombre por defecto
            gdf_localidad['nombre'] = 'Barrios Unidos'
    else:
        print(f"❌ No se encuentra el archivo: {RUTA_LOCALIDAD}")
except Exception as e:
    print(f"❌ Error cargando localidad: {e}")


# Cargar estaciones
try:
    if os.path.exists(RUTA_ESTACIONES):
        gdf_estaciones = gpd.read_file(RUTA_ESTACIONES)
        estaciones_data = json.loads(gdf_estaciones.to_json())
        print(f"\n✅ Estaciones cargadas: {RUTA_ESTACIONES}")
        print(f"   Total estaciones: {len(gdf_estaciones)}")
        print(f"   Columnas: {list(gdf_estaciones.columns)}")
       
        # Filtrar estaciones de Barrios Unidos si es posible
        estaciones_barrios = []
        for idx, row in gdf_estaciones.iterrows():
            if 'localidad' in gdf_estaciones.columns:
                if row['localidad'] and 'Barrios Unidos' in str(row['localidad']):
                    estaciones_barrios.append(row)
            else:
                estaciones_barrios.append(row)
       
        if estaciones_barrios:
            print(f"   Estaciones en Barrios Unidos: {len(estaciones_barrios)}")
            gdf_estaciones_filtrado = gpd.GeoDataFrame(estaciones_barrios)
        else:
            print("   ⚠️ No se pudo filtrar por localidad, usando todas")
            gdf_estaciones_filtrado = gdf_estaciones
    else:
        print(f"❌ No se encuentra el archivo: {RUTA_ESTACIONES}")
        gdf_estaciones_filtrado = None
except Exception as e:
    print(f"❌ Error cargando estaciones: {e}")
    gdf_estaciones_filtrado = None


# Generar puntos de interés alrededor de las estaciones
if gdf_estaciones_filtrado is not None and len(gdf_estaciones_filtrado) > 0:
    print("\n🔄 Generando puntos de interés...")
    for idx, estacion in gdf_estaciones_filtrado.iterrows():
        if hasattr(estacion.geometry, 'x'):  # Verificar que tiene geometría
            for i in range(random.randint(1, 3)):  # 1-3 puntos por estación
                angulo = random.uniform(0, 2 * pi)
                distancia = random.uniform(20, 80) / 111000  # 20-80 metros
               
                dlat = distancia * cos(angulo)
                dlon = distancia * sin(angulo) / cos(radians(estacion.geometry.y))
               
                puntos_interes.append({
                    'id': len(puntos_interes),
                    'nombre': f"{random.choice(['Bar', 'Restaurante', 'Café', 'Empanadas'])} {idx}-{i}",
                    'tipo': random.choice(['bar', 'empanadas']),
                    'lon': estacion.geometry.x + dlon,
                    'lat': estacion.geometry.y + dlat,
                    'direccion': f"Calle {random.randint(1,100)} #{random.randint(1,50)}",
                    'estacion_id': idx
                })
    print(f"✅ {len(puntos_interes)} puntos de interés generados")
else:
    print("⚠️ No se generaron puntos de interés")


print("\n" + "=" * 60)
print("✅ SERVIDOR LISTO")
print(f"📍 Localidad: Barrios Unidos")
print(f"🚏 Estaciones: {len(gdf_estaciones_filtrado) if gdf_estaciones_filtrado is not None else 0}")
print(f"🍔 Puntos de interés: {len(puntos_interes)}")
print("=" * 60)


def calcular_distancia(lon1, lat1, lon2, lat2):
    """Distancia aproximada en metros"""
    return sqrt((lon2-lon1)**2 + (lat2-lat1)**2) * 111000


@app.get("/")
def read_root():
    return {
        "mensaje": "API de Barrios Unidos - SITP",
        "localidad": "Barrios Unidos",
        "estaciones_cargadas": len(gdf_estaciones_filtrado) if gdf_estaciones_filtrado is not None else 0,
        "puntos_interes": len(puntos_interes)
    }


@app.get("/api/localidades")
def get_localidades():
    """Lista de localidades (solo Barrios Unidos)"""
    return [{
        "id": 1,
        "nombre": "Barrios Unidos",
        "area": 12.5,
        "poblacion": 250000
    }]


@app.get("/api/localidades/{nombre}")
def get_localidad_info(nombre: str):
    """Información de Barrios Unidos"""
    # Extraer estaciones
    estaciones_lista = []
    if gdf_estaciones_filtrado is not None:
        for idx, row in gdf_estaciones_filtrado.iterrows():
            estaciones_lista.append({
                "id": idx,
                "nombre": row.get('nombre', f'Estación {idx}'),
                "codigo": row.get('codigo', f'COD-{idx}'),
                "direccion": row.get('direccion', 'Dirección no disponible')
            })
   
    return {
        "id": 1,
        "nombre": "Barrios Unidos",
        "area": 12.5,
        "poblacion": 250000,
        "estaciones": estaciones_lista
    }


@app.get("/api/localidades")
def get_localidades():
    """Lista de localidades (solo Barrios Unidos)"""
    print("📨 Petición recibida: /api/localidades")
    return [{
        "id": 1,
        "nombre": "Barrios Unidos",
        "area": 12.5,
        "poblacion": 250000
    }]


@app.get("/api/geojson/estaciones/{localidad}")
def get_estaciones_geojson(localidad: str):
    """GeoJSON de estaciones"""
    if gdf_estaciones_filtrado is not None:
        return json.loads(gdf_estaciones_filtrado.to_json())
    else:
        return {"type": "FeatureCollection", "features": []}


@app.get("/api/estaciones")
def get_todas_estaciones():
    """Lista de todas las estaciones"""
    estaciones_lista = []
    if gdf_estaciones_filtrado is not None:
        for idx, row in gdf_estaciones_filtrado.iterrows():
            estaciones_lista.append({
                "id": idx,
                "nombre": row.get('nombre', f'Estación {idx}'),
                "codigo": row.get('codigo', f'COD-{idx}'),
                "localidad": "Barrios Unidos"
            })
    return estaciones_lista


@app.get("/api/puntos_interes")
def get_puntos_interes():
    """GeoJSON de puntos de interés"""
    features = []
    for punto in puntos_interes:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [punto['lon'], punto['lat']]
            },
            "properties": {
                "id": punto['id'],
                "nombre": punto['nombre'],
                "tipo": punto['tipo'],
                "direccion": punto['direccion']
            }
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/analisis/estacion/{estacion_id}")
def analizar_estacion(estacion_id: int, buffer_metros: int = 100):
    """Analizar estación específica"""
    if gdf_estaciones_filtrado is None or estacion_id >= len(gdf_estaciones_filtrado):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
   
    estacion = gdf_estaciones_filtrado.iloc[estacion_id]
   
    if not hasattr(estacion.geometry, 'x'):
        raise HTTPException(status_code=400, detail="Estación sin geometría válida")
   
    # Buscar puntos dentro del buffer
    bares = 0
    empanadas = 0
    puntos_encontrados = []
   
    for punto in puntos_interes:
        dist = calcular_distancia(
            estacion.geometry.x, estacion.geometry.y,
            punto['lon'], punto['lat']
        )
        if dist <= buffer_metros:
            puntos_encontrados.append(punto)
            if punto['tipo'] == 'bar':
                bares += 1
            else:
                empanadas += 1
   
    # Crear círculo del buffer
    circulo = []
    for i in range(37):
        angulo = 2 * pi * i / 36
        radio_grados = buffer_metros / 111000
        dlat = radio_grados * cos(angulo)
        dlon = radio_grados * sin(angulo) / cos(radians(estacion.geometry.y))
        circulo.append([estacion.geometry.x + dlon, estacion.geometry.y + dlat])
   
    return {
        "estacion": {
            "id": estacion_id,
            "nombre": estacion.get('nombre', f'Estación {estacion_id}'),
            "codigo": estacion.get('codigo', f'COD-{estacion_id}')
        },
        "estadisticas": {
            "bares": bares,
            "puestos_empanadas": empanadas,
            "total": bares + empanadas
        },
        "puntos_interes": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [p['lon'], p['lat']]},
                "properties": {
                    "nombre": p['nombre'],
                    "tipo": p['tipo'],
                    "direccion": p['direccion']
                }
            } for p in puntos_encontrados]
        },
        "buffer_geom": {
            "type": "Polygon",
            "coordinates": [circulo]
        }
    }
