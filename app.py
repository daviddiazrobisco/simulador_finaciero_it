import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

# 📂 Cargar datos
with open("data/presupuesto_it_2025.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

with open("data/resumen_benchmark.json", "r", encoding="utf-8") as f:
    benchmark = json.load(f)

# 📌 Extraer datos generales
empresa = datos["empresa"]
anio = datos["anio"]
param = datos["parametros"]
res = datos["resultados"]

# 🎨 Estilos
st.set_page_config(page_title="Simulador PyG IT", layout="wide")

st.title(f"📊 Simulador PyG – {empresa} ({anio})")

# ---------------------
# 🔵 VISIÓN GENERAL
# ---------------------
st.header("🔵 Visión General")
col1, col2, col3, col4 = st.columns(4)

# KPIs
col1.metric("Facturación Total", f"{res['facturacion_total']:,} €")
col2.metric("Margen Bruto", f"{res['margen_bruto']:,} € ({(res['margen_bruto']/res['facturacion_total'])*100:.1f}%)",
            f"Benchmark: {benchmark['margen_bruto_%']}%")
col3.metric("Costes Fijos", f"{res['costes_fijos']:,} € ({(res['costes_fijos']/res['facturacion_total'])*100:.1f}%)",
            f"Benchmark: {benchmark['costes_fijos_%']}%")
col4.metric("EBITDA", f"{res['ebitda']:,} € ({res['ebitda_%']:.1f}%)",
            f"Benchmark: {benchmark['ebitda_%']}%")

# Alertas
if res["subactividad"]["utilizacion_real_%"] < benchmark["utilizacion_%"]:
    st.warning(f"⚠️ Utilización baja: {res['subactividad']['utilizacion_real_%']}% vs Benchmark {benchmark['utilizacion_%']}%")
if (res['margen_bruto']/res['facturacion_total'])*100 < benchmark["margen_bruto_%"]:
    st.error("❗ Margen Bruto por debajo del benchmark")

# Waterfall PyG
st.subheader("💸 Cuenta de Resultados (Waterfall)")
fig, ax = plt.subplots(figsize=(8,4))
labels = ["Ingresos", "Costes Directos", "Margen Bruto", "Costes Fijos", "EBITDA"]
values = [
    res['facturacion_total'],
    -res['costes_directos'],
    res['margen_bruto'],
    -res['costes_fijos'],
    res['ebitda']
]
ax.bar(labels, values, color=["green", "red", "green", "red", "blue"])
ax.set_ylabel("€")
st.pyplot(fig)

# ---------------------
# 🟧 ANÁLISIS LÍNEA NEGOCIO
# ---------------------
st.header("🟧 Análisis por Línea de Negocio")
lineas = list(param["lineas_negocio"].keys())
linea_seleccionada = st.selectbox("Selecciona línea de negocio", lineas)

ln = param["lineas_negocio"][linea_seleccionada]

# KPIs Línea
st.subheader(f"📊 KPIs: {linea_seleccionada}")
col5, col6, col7 = st.columns(3)
margen_bruto_ln = ln["tarifa"] * ln["unidades"] - ln["costes_directos_%"]/100 * (ln["tarifa"] * ln["unidades"])
utilizacion = res["subactividad"]["utilizacion_real_%"]

col5.metric("Tarifa (€/día)", f"{ln['tarifa']:,}",
            f"Benchmark: {benchmark['tarifa_eur_dia']} €")
col6.metric("Coste Medio Personal", f"{ln['coste_medio_persona']:,} €",
            f"Benchmark: {benchmark['coste_medio_persona_eur']} €")
col7.metric("Utilización (%)", f"{utilizacion}%",
            f"Benchmark: {benchmark['utilizacion_%']}%")

# 🎛️ Sliders de simulación
st.subheader("🎛️ Simula ajustes:")
tarifa = st.slider("Tarifa (€/día)", 0, 2000, ln["tarifa"], step=50)
proyectos = st.slider("Nº Proyectos", 0, 50, ln["unidades"])
coste_personal = st.slider("Coste Medio Personal (€)", 30000, 90000, ln["coste_medio_persona"], step=5000)
subactividad = st.slider("Subactividad (%)", 0, 30, param["subactividad_permitida_%"])

# Nuevo cálculo margen bruto
ingresos_simulados = tarifa * proyectos
costes_directos_simulados = (coste_personal * ln["personas"]) + (ln["costes_directos_%"]/100 * ingresos_simulados)
margen_bruto_simulado = ingresos_simulados - costes_directos_simulados

st.success(f"📈 Nuevo Margen Bruto Simulado: {margen_bruto_simulado:,.0f} €")

if subactividad > benchmark["subactividad_max_%"]:
    st.warning(f"⚠️ Subactividad alta: {subactividad}% vs Benchmark {benchmark['subactividad_max_%']}%")

# Gráfico de barras
st.subheader("📊 Ingresos vs Costes Directos")
fig2, ax2 = plt.subplots()
ax2.bar(["Ingresos", "Costes Directos"], [ingresos_simulados, costes_directos_simulados], color=["green", "red"])
st.pyplot(fig2)
