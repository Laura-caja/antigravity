// Configuración del mapa
const map = L.map('map').setView([4.663, -74.07], 14); // Centrado en Barrios Unidos

// Capa base de OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

// Variables globales
let capaLocalidad = null;
let capaEstaciones = null;
let capaPuntosInteres = null;
let capaBuffer = null;
let todasEstaciones = [];
let puntosInteres = [];

// URL base de la API
const API_URL = 'http://localhost:8000';

// Inicialización
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Iniciando aplicación...');
    
    // Mostrar que el mapa está cargando
    map.invalidateSize();
    
    await cargarInformacionInicial();
    configurarEventos();
});

async function cargarInformacionInicial() {
    try {
        // Cargar información de Barrios Unidos
        const infoResponse = await fetch(`${API_URL}/api/localidades/Barrios Unidos`);
        const info = await infoResponse.json();
        
        // Actualizar panel de información
        document.getElementById('localidad-info').innerHTML = `
            <p><strong>🏘️ Nombre:</strong> ${info.nombre}</p>
            <p><strong>📏 Área:</strong> ${info.area} km²</p>
            <p><strong>👥 Población:</strong> ${info.poblacion.toLocaleString()}</p>
        `;
        
        // Guardar estaciones
        todasEstaciones = info.estaciones || [];
        
        // Llenar selector de estaciones
        const selectEstacion = document.getElementById('estacion-analisis');
        selectEstacion.innerHTML = '<option value="">Seleccione una estación</option>';
        todasEstaciones.forEach(estacion => {
            const option = document.createElement('option');
            option.value = estacion.id;
            option.textContent = estacion.nombre;
            selectEstacion.appendChild(option);
        });
        
        // Mostrar lista de estaciones
        const estacionesLista = document.getElementById('estaciones-lista');
        if (todasEstaciones.length > 0) {
            let html = '';
            todasEstaciones.forEach(estacion => {
                html += `
                    <div class="estacion-item" onclick="seleccionarEstacion(${estacion.id})" style="padding: 8px; margin: 5px 0; background: #f0f0f0; border-radius: 4px; cursor: pointer;">
                        🚏 ${estacion.nombre} <small>(${estacion.codigo})</small>
                    </div>
                `;
            });
            estacionesLista.innerHTML = html;
        }
        
        // Cargar puntos de interés
        const puntosResponse = await fetch(`${API_URL}/api/puntos_interes`);
        const puntosData = await puntosResponse.json();
        puntosInteres = puntosData.features || [];
        
        // Cargar GeoJSON de la localidad
        await cargarLocalidadGeoJSON();
        
        // Cargar GeoJSON de estaciones
        await cargarEstacionesGeoJSON();
        
        console.log('✅ Todo cargado correctamente');
        
    } catch (error) {
        console.error('❌ Error:', error);
        document.getElementById('localidad-info').innerHTML = '<p style="color: red;">Error cargando datos</p>';
    }
}

async function cargarLocalidadGeoJSON() {
    try {
        const response = await fetch(`${API_URL}/api/geojson/localidad/Barrios Unidos`);
        const geojson = await response.json();
        
        if (capaLocalidad) map.removeLayer(capaLocalidad);
        
        capaLocalidad = L.geoJSON(geojson, {
            style: {
                color: '#e67e22',
                weight: 3,
                fillColor: '#f39c12',
                fillOpacity: 0.2
            }
        }).addTo(map);
        
        // Ajustar vista
        map.fitBounds(capaLocalidad.getBounds(), { padding: [50, 50] });
        
    } catch (error) {
        console.error('Error cargando localidad:', error);
    }
}

async function cargarEstacionesGeoJSON() {
    try {
        const response = await fetch(`${API_URL}/api/geojson/estaciones/Barrios Unidos`);
        const geojson = await response.json();
        
        if (capaEstaciones) map.removeLayer(capaEstaciones);
        
        capaEstaciones = L.geoJSON(geojson, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng, {
                    icon: L.divIcon({
                        className: 'estacion-marker',
                        html: '🚏',
                        iconSize: [30, 30]
                    })
                });
            },
            onEachFeature: function(feature, layer) {
                layer.bindPopup(`
                    <b>${feature.properties.nombre}</b><br>
                `);
            }
        }).addTo(map);
        
    } catch (error) {
        console.error('Error cargando estaciones:', error);
    }
}

async function analizarEstacion(estacionId) {
    try {
        document.getElementById('btn-analizar').textContent = '⏳ Analizando...';
        
        const response = await fetch(`${API_URL}/api/analisis/estacion/${estacionId}?buffer_metros=100`);
        const resultado = await response.json();
        
        // Mostrar resultados
        document.getElementById('resultado-analisis').innerHTML = `
            <h4>📊 ${resultado.estacion.nombre}</h4>
            <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                <p>🍺 Bares: <strong>${resultado.estadisticas.bares}</strong></p>
                <p>🥟 Empanadas: <strong>${resultado.estadisticas.puestos_empanadas}</strong></p>
                <p>📌 Total: <strong style="color:#27ae60;">${resultado.estadisticas.total}</strong></p>
            </div>
        `;
        
        // Mostrar en el mapa
        if (capaBuffer) map.removeLayer(capaBuffer);
        if (capaPuntosInteres) map.removeLayer(capaPuntosInteres);
        
        // Buffer
        capaBuffer = L.geoJSON(resultado.buffer_geom, {
            style: {
                color: '#27ae60',
                weight: 2,
                fillColor: '#2ecc71',
                fillOpacity: 0.1
            }
        }).addTo(map);
        
        // Puntos de interés
        if (resultado.puntos_interes.features.length > 0) {
            capaPuntosInteres = L.geoJSON(resultado.puntos_interes, {
                pointToLayer: function(feature, latlng) {
                    const icon = feature.properties.tipo === 'bar' ? '🍺' : '🥟';
                    return L.marker(latlng, {
                        icon: L.divIcon({
                            className: 'poi-marker',
                            html: icon,
                            iconSize: [25, 25]
                        })
                    });
                }
            }).addTo(map);
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error al analizar la estación');
    } finally {
        document.getElementById('btn-analizar').textContent = '🔍 Analizar';
    }
}

function seleccionarEstacion(id) {
    document.getElementById('estacion-analisis').value = id;
    analizarEstacion(id);
}

// Eventos
function configurarEventos() {
    document.getElementById('btn-analizar').addEventListener('click', function() {
        const id = document.getElementById('estacion-analisis').value;
        if (id) analizarEstacion(parseInt(id));
        else alert('Seleccione una estación');
    });
    
    // Control de capas
    document.getElementById('layer-localidad').addEventListener('change', function(e) {
        if (capaLocalidad) {
            if (e.target.checked) map.addLayer(capaLocalidad);
            else map.removeLayer(capaLocalidad);
        }
    });
    
    document.getElementById('layer-estaciones').addEventListener('change', function(e) {
        if (capaEstaciones) {
            if (e.target.checked) map.addLayer(capaEstaciones);
            else map.removeLayer(capaEstaciones);
        }
    });
    
    document.getElementById('layer-puntos-interes').addEventListener('change', function(e) {
        if (capaPuntosInteres) {
            if (e.target.checked) map.addLayer(capaPuntosInteres);
            else map.removeLayer(capaPuntosInteres);
        }
    });
    
    document.getElementById('layer-buffer').addEventListener('change', function(e) {
        if (capaBuffer) {
            if (e.target.checked) map.addLayer(capaBuffer);
            else map.removeLayer(capaBuffer);
        }
    });
}

// Hacer funciones globales
window.analizarEstacion = analizarEstacion;
window.seleccionarEstacion = seleccionarEstacion;