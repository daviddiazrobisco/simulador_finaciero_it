import streamlit as st
import json

# --- Cargar JSON inicial ---
with open("datos.json", "r") as f:
    data = json.load(f)

# --- Título y descripción ---
st.title(f"Simulador Financiero - {data['empresa']} ({data['anio']})")
st.write("Ajusta los parámetros para ver el impacto en facturación, margen, EBITDA y utilización de equipos.")

# --- Sliders por línea de negocio ---
st.header("📊 Parámetros - Líneas de Negocio")
for linea, valores in data['parametros']['lineas_negocio'].items():
    st.subheader(linea)
    valores['tarifa'] = st.slider(f"Tarifa {linea} (€)", 0, 2000, valores['tarifa'], 50)
    valores['unidades'] = st.number_input(f"Nº {linea} (proyectos/licencias/contratos)", 0, 100, valores['unidades'])
    if valores['personas'] > 0:
        valores['personas'] = st.number_input(f"Personas dedicadas a {linea}", 0, 200, valores['personas'])
        valores['jornadas_por_persona'] = st.number_input(f"Jornadas/año por persona en {linea}", 0, 300, valores['jornadas_por_persona'])
        valores['coste_medio_persona'] = st.number_input(f"Coste medio persona en {linea} (€)", 0, 100000, valores['coste_medio_persona'], 1000)

# --- Sliders de costes fijos ---
st.header("📊 Parámetros - Costes Fijos")
for coste, valor in data['parametros']['costes_fijos'].items():
    data['parametros']['costes_fijos'][coste] = st.number_input(f"{coste.capitalize()} (€)", 0, 500000, int(valor), 1000)

# --- Cálculos completos ---
facturacion_total = 0
jornadas_disponibles_totales = 0
jornadas_necesarias_totales = 0
costes_directos_totales = 0

for linea, valores in data['parametros']['lineas_negocio'].items():
    # Facturación por línea
    facturacion_linea = valores['unidades'] * valores['ticket_medio']
    facturacion_total += facturacion_linea

    # Jornadas necesarias para los proyectos/licencias
    if valores['tarifa'] > 0:
        jornadas_necesarias = facturacion_linea / valores['tarifa']
    else:
        jornadas_necesarias = 0
    jornadas_necesarias_totales += jornadas_necesarias

    # Jornadas disponibles (personas × jornadas/año)
    jornadas_disponibles = valores['personas'] * valores['jornadas_por_persona']
    jornadas_disponibles_totales += jornadas_disponibles

    # Coste directo (personas × coste medio)
    coste_directo_linea = valores['personas'] * valores['coste_medio_persona']
    costes_directos_totales += coste_directo_linea

# Subactividad (si jornadas disponibles > necesarias)
subactividad_jornadas = max(jornadas_disponibles_totales - jornadas_necesarias_totales, 0)
subactividad_coste = (subactividad_jornadas / jornadas_disponibles_totales) * costes_directos_totales if jornadas_disponibles_totales else 0

# Margen bruto y EBITDA
margen_bruto = facturacion_total - costes_directos_totales
costes_fijos_totales = sum(data['parametros']['costes_fijos'].values())
ebitda = margen_bruto - costes_fijos_totales
ebitda_pct = (ebitda / facturacion_total) * 100 if facturacion_total else 0

# Utilización real
utilizacion_real = (jornadas_necesarias_totales / jornadas_disponibles_totales * 100) if jornadas_disponibles_totales else 0

# --- Mostrar resultados ---
st.header("📈 Resultados")
st.metric("Facturación Total", f"{facturacion_total:,.0f} €")
st.metric("Margen Bruto", f"{margen_bruto:,.0f} € ({(margen_bruto/facturacion_total)*100:.1f}%)")
st.metric("EBITDA", f"{ebitda:,.0f} € ({ebitda_pct:.1f}%)")
st.metric("Utilización del equipo", f"{utilizacion_real:.1f}%")
st.metric("Subactividad (coste)", f"{subactividad_coste:,.0f} €")

# Alertas visuales
if utilizacion_real < 50:
    st.error("⚠️ Baja utilización: riesgo alto de subactividad")
elif utilizacion_real < 70:
    st.warning("🟡 Utilización moderada: posible subactividad")
else:
    st.success("✅ Buena utilización del equipo")

# --- Descargar JSON actualizado ---
if st.button("📥 Descargar JSON Actualizado"):
    with open("json_actualizado.json", "w") as out:
        json.dump(data, out, indent=4)
    st.success("JSON actualizado guardado.")
