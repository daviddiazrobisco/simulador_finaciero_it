import streamlit as st
import json
import plotly.graph_objects as go

# --- Cargar JSON inicial ---
with open("datos.json", "r") as f:
    data = json.load(f)

# --- Título y descripción ---
st.title(f"📊 Simulador Financiero - {data['empresa']} ({data['anio']})")
st.markdown("Ajusta los parámetros para ver el impacto en facturación, margen, EBITDA y utilización de equipos con gráficos en tiempo real.")

# --- Sliders por línea de negocio ---
st.header("🎛️ Parámetros - Líneas de Negocio")
for linea, valores in data['parametros']['lineas_negocio'].items():
    st.subheader(f"🔹 {linea}")
    valores['tarifa'] = st.slider(f"Tarifa {linea} (€)", 0, 2000, valores['tarifa'], 50)
    valores['unidades'] = st.number_input(f"Nº {linea} (proyectos/licencias/contratos)", 0, 100, valores['unidades'])
    if valores['personas'] > 0:
        valores['personas'] = st.number_input(f"Personas dedicadas a {linea}", 0, 200, valores['personas'])
        valores['jornadas_por_persona'] = st.number_input(f"Jornadas/año por persona en {linea}", 0, 300, valores['jornadas_por_persona'])
        valores['coste_medio_persona'] = st.number_input(f"Coste medio persona en {linea} (€)", 0, 100000, valores['coste_medio_persona'], 1000)

# --- Sliders de costes fijos ---
st.header("🎛️ Parámetros - Costes Fijos")
for coste, valor in data['parametros']['costes_fijos'].items():
    data['parametros']['costes_fijos'][coste] = st.number_input(f"{coste.capitalize()} (€)", 0, 500000, int(valor), 1000)

# --- Cálculos completos ---
facturacion_total = 0
jornadas_disponibles_totales = 0
jornadas_necesarias_totales = 0
costes_directos_totales = 0
facturacion_lineas = {}
utilizacion_lineas = {}

for linea, valores in data['parametros']['lineas_negocio'].items():
    # Facturación por línea
    facturacion_linea = valores['unidades'] * valores['ticket_medio']
    facturacion_lineas[linea] = facturacion_linea
    facturacion_total += facturacion_linea

    # Jornadas necesarias
    jornadas_necesarias = facturacion_linea / valores['tarifa'] if valores['tarifa'] else 0
    jornadas_necesarias_totales += jornadas_necesarias

    # Jornadas disponibles
    jornadas_disponibles = valores['personas'] * valores['jornadas_por_persona']
    jornadas_disponibles_totales += jornadas_disponibles

    # Utilización por línea
    utilizacion = (jornadas_necesarias / jornadas_disponibles * 100) if jornadas_disponibles else 0
    utilizacion_lineas[linea] = round(utilizacion, 1)

    # Coste directo
    coste_directo_linea = valores['personas'] * valores['coste_medio_persona']
    costes_directos_totales += coste_directo_linea

# Subactividad
subactividad_jornadas = max(jornadas_disponibles_totales - jornadas_necesarias_totales, 0)
subactividad_coste = (subactividad_jornadas / jornadas_disponibles_totales) * costes_directos_totales if jornadas_disponibles_totales else 0

# Margen y EBITDA
margen_bruto = facturacion_total - costes_directos_totales
costes_fijos_totales = sum(data['parametros']['costes_fijos'].values())
ebitda = margen_bruto - costes_fijos_totales
ebitda_pct = (ebitda / facturacion_total) * 100 if facturacion_total else 0

# Utilización global
utilizacion_global = (jornadas_necesarias_totales / jornadas_disponibles_totales * 100) if jornadas_disponibles_totales else 0

# --- Mostrar métricas principales ---
st.header("📈 Resultados Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Facturación Total", f"{facturacion_total:,.0f} €")
col2.metric("Margen Bruto", f"{margen_bruto:,.0f} € ({(margen_bruto/facturacion_total)*100:.1f}%)")
col3.metric("EBITDA", f"{ebitda:,.0f} € ({ebitda_pct:.1f}%)")

st.metric("Utilización Global del Equipo", f"{utilizacion_global:.1f}%")
st.metric("Subactividad (coste)", f"{subactividad_coste:,.0f} €")

# Alertas visuales
if utilizacion_global < 50:
    st.error("⚠️ Baja utilización: riesgo alto de subactividad")
elif utilizacion_global < 70:
    st.warning("🟡 Utilización moderada: posible subactividad")
else:
    st.success("✅ Buena utilización del equipo")

# --- Gráficos dinámicos ---
st.header("📊 Visualizaciones")

# Gráfico 1: Facturación por línea
fig1 = go.Figure([go.Bar(x=list(facturacion_lineas.keys()), y=list(facturacion_lineas.values()))])
fig1.update_layout(title="Facturación por Línea de Negocio", xaxis_title="Línea", yaxis_title="Facturación (€)")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Utilización por línea
fig2 = go.Figure([go.Bar(x=list(utilizacion_lineas.keys()), y=list(utilizacion_lineas.values()), marker_color='orange')])
fig2.update_layout(title="Utilización por Línea de Negocio (%)", xaxis_title="Línea", yaxis_title="Utilización (%)")
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: EBITDA vs Costes
fig3 = go.Figure()
fig3.add_trace(go.Bar(name="EBITDA", x=["EBITDA"], y=[ebitda]))
fig3.add_trace(go.Bar(name="Costes Fijos", x=["Costes Fijos"], y=[costes_fijos_totales]))
fig3.update_layout(title="EBITDA vs Costes Fijos", barmode='group', yaxis_title="€")
st.plotly_chart(fig3, use_container_width=True)

# --- Botón para descargar JSON actualizado ---
if st.button("📥 Descargar JSON Actualizado"):
    with open("json_actualizado.json", "w") as out:
        json.dump(data, out, indent=4)
    st.success("JSON actualizado guardado.")
