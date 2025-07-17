import streamlit as st
import json

# --- Cargar JSON inicial ---
with open("datos.json", "r") as f:
    data = json.load(f)

# --- Título y descripción ---
st.title(f"Simulador Financiero - {data['empresa']} ({data['anio']})")
st.write("Ajusta los parámetros para ver impacto en margen bruto, EBITDA y utilización de equipos.")

# --- Sliders por línea de negocio ---
st.header("Parámetros - Líneas de Negocio")
for linea, valores in data['parametros']['lineas_negocio'].items():
    st.subheader(linea)
    valores['tarifa'] = st.slider(f"Tarifa {linea} (€)", 0, 2000, valores['tarifa'], 50)
    valores['unidades'] = st.number_input(f"Nº {linea} (proyectos/licencias/contratos)", 0, 100, valores['unidades'])
    if valores['personas'] > 0:
        valores['personas'] = st.number_input(f"Personas dedicadas a {linea}", 0, 100, valores['personas'])
        valores['coste_medio_persona'] = st.number_input(f"Coste medio por persona en {linea} (€)", 0, 100000, valores['coste_medio_persona'], 1000)

# --- Sliders de costes fijos ---
st.header("Parámetros - Costes Fijos")
for coste, valor in data['parametros']['costes_fijos'].items():
    data['parametros']['costes_fijos'][coste] = st.number_input(f"{coste.capitalize()} (€)", 0, 500000, int(valor), 1000)

# --- Cálculos simplificados ---
facturacion_total = 0
costes_directos = 0

for linea, valores in data['parametros']['lineas_negocio'].items():
    facturacion_linea = valores['unidades'] * valores['ticket_medio']
    coste_directo_linea = facturacion_linea * (valores['costes_directos_%'] / 100)
    facturacion_total += facturacion_linea
    costes_directos += coste_directo_linea

margen_bruto = facturacion_total - costes_directos
costes_fijos = sum(data['parametros']['costes_fijos'].values())
ebitda = margen_bruto - costes_fijos
ebitda_pct = (ebitda / facturacion_total) * 100 if facturacion_total > 0 else 0

# --- Mostrar resultados ---
st.header("📊 Resultados")
st.metric("Facturación Total", f"{facturacion_total:,.0f} €")
st.metric("Margen Bruto", f"{margen_bruto:,.0f} € ({(margen_bruto/facturacion_total)*100:.1f}%)")
st.metric("Costes Fijos", f"{costes_fijos:,.0f} €")
st.metric("EBITDA", f"{ebitda:,.0f} € ({ebitda_pct:.1f}%)")

# --- Descargar JSON actualizado ---
if st.button("📥 Descargar JSON Actualizado"):
    with open("json_actualizado.json", "w") as out:
        json.dump(data, out, indent=4)
    st.success("JSON actualizado guardado.")
