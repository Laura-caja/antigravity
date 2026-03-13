# cargar_datos.py
import geopandas as gpd
from sqlalchemy import create_engine
import random

# Configuración de conexión - CAMBIA LA CONTRASEÑA
DB_USER = "postgres"
DB_PASSWORD = "4103"  # ← CAMBIA ESTO por tu contraseña real
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bogota_db"

print("Conectando a la base de datos...")
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# 1. Cargar localidad (usando GeoJSON.json)
print("Cargando localidad...")
try:
    # NOTA: Estoy asumiendo que GeoJSON.json es el archivo de la localidad
    # Si no es así, cámbialo por el nombre correcto
    gdf_localidad = gpd.read_file("datos/GeoJSON.json")
    gdf_localidad.to_postgis("localidades", engine, if_exists='replace', index=False)
    print("✓ Localidad cargada exitosamente")
except Exception as e:
    print(f"✗ Error cargando localidad: {e}")

# 2. Cargar estaciones SITP (usando paradero_zonal.geojson)
print("\nCargando estaciones SITP...")
try:
    gdf_estaciones = gpd.read_file("datos/paradero_zonal.geojson")
    gdf_estaciones.to_postgis("estaciones_sitp", engine, if_exists='replace', index=False)
    print("✓ Estaciones cargadas exitosamente")
except Exception as e:
    print(f"✗ Error cargando estaciones: {e}")

# 3. Crear datos de ejemplo para bares y empanadas
print("\nCreando datos de ejemplo de bares y empanadas...")
try:
    if 'gdf_estaciones' in locals() and len(gdf_estaciones) > 0:
        bares_data = []
        for idx, estacion in gdf_estaciones.iterrows():
            for i in range(random.randint(0, 3)):
                lon = estacion.geometry.x + random.uniform(-0.001, 0.001)
                lat = estacion.geometry.y + random.uniform(-0.001, 0.001)
                bares_data.append({
                    'nombre': f"Establecimiento {idx}-{i}",
                    'direccion': f"Calle {random.randint(1,100)} #{random.randint(1,50)}-{random.randint(1,50)}",
                    'tipo': random.choice(['bar', 'empanadas']),
                    'geometry': f'POINT({lon} {lat})'
                })
        
        if bares_data:
            gdf_bares = gpd.GeoDataFrame(bares_data, crs="EPSG:4326")
            gdf_bares.to_postgis("bares", engine, if_exists='replace', index=False)
            print(f"✓ {len(bares_data)} puntos de interés creados")
        else:
            print("! No se generaron puntos de interés")
    else:
        print("! No hay estaciones para generar puntos de interés")
        
except Exception as e:
    print(f"✗ Error creando datos de ejemplo: {e}")

print("\n✅ Proceso completado!")