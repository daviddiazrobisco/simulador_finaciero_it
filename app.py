import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

# 🌍 Función personalizada para formato europeo
def formato_eur(valor):
    try:
        valor_abs = abs(valor)
        partes = f"{valor_abs:,.2f}".split(".")
        entero = partes[0].replace(",", ".")
        decimal = partes[1]
        formato = f"{entero},{decimal}"
        if valor < 0:
            return f":red[({formato})]"
        else:
            return formato
    except:
        return valor

# 🎨 Estilos personalizados
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Nunito Sans', sans-serif;
        background-color: #FFFFFF;
        color: #333333;
    }
    .st-bb, .st-bf, .st-dc, .st-cz, .st-ag {
        background-color: #F2F2F2 !important;
    }
    .st-bf {
        border-radius: 8px;
        padding: 10px;
    }
    .css-1d391kg {
        background-color: #144C44;
        color: #FFFFFF;
        font-size: 1.5em;
    }
    .stButton>button {
        background-color: #fb9200;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 1em;
    }
    .stButton>button:hover {
        background-color: #e67e00;
    }
    .metric-label {
        color: #144C44 !important;
        font-weight: bold;
    }
    .metric-value {
        font-size: 2.0em !important;
        color: #333333;
    }
    .metric-delta {
        font-size: 0.9em !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# 🎯 Título
st.title(f"📊 Simulador PyG – {empresa} ({anio})")

# ---------------------
# 🔵 VISIÓN GENERAL
# ---------------------
st.header("🔵 Visión General")
col1, col2, col3, col4 = st.columns(4)

# KPIs con formato europeo
col1.metric("Facturación Total", f"{formato_eur(res['facturacion_total'])} €")
col2.metric("Margen Bruto", f"{formato_eur(res['margen_bruto'])} € ({(res['margen_bruto']/res['facturacion_total'])*100:.1f}%)",
            f"Benchmark: {benchmark['margen_bruto_%']}%")
col3.metric("Costes Fijos", f"{formato_eur(res['costes_fijos'])} € ({(res['costes_fijos']/res['facturacion_total'])*100:.1f}%)",
            f"Benchmark: {benchmark['costes_fijos_%']}%")
col4.metric("EBITDA", f"{formato_eur(res['ebitda'])} € ({res['ebitda_%']:.1f}%)",
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
colors = ["#144C44", "#fb9200", "#144C44", "#fb9200", "#144C44"]
bars = ax.bar(labels, values, color=colors)
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            formato_eur(value), ha='center', va='bottom', fontsize=10)
ax.set_ylabel("€")
st.pyplot(fig)

# ---------------------
# 🟧 ANÁLISIS LÍNEA DE NEGOCIO
# ---------------------
st.header("🟧 Análisis por Línea de Negocio")
lineas = list(param["lineas_negocio"].keys())
linea_seleccionada = st.selectbox("Selecciona línea de negocio", lineas)

ln = param["lineas_negocio"][linea_seleccionada]

# KPIs Línea
st.subheader(f"📊 KPIs: {linea_seleccionada}")
col5, col6, col7, col8 = st.columns(4)
col5.metric("Tarifa (€/día)", f"{formato_eur(ln['tarifa'])} €",
            f"Benchmark: {formato_eur(benchmark['tarifa_eur_dia'])} €")
col6.metric("Coste Medio Personal", f"{formato_eur(ln['coste_medio_persona'])} €",
            f"Benchmark: {formato_eur(benchmark['coste_medio_persona_eur'])} €")
col7.metric("Personas", ln["personas"])
col8.metric("Utilización (%)", f"{res['subactividad']['utilizacion_real_%']}%",
            f"Benchmark: {benchmark['utilizacion_%']}%")

# 🎛️ Sliders de simulación
st.subheader("🎛️ Simula ajustes:")
tarifa = st.slider("Tarifa (€/día)", 0, 2000, ln["tarifa"], step=50)
proyectos = st.slider("Nº Proyectos", 0, 50, ln["unidades"])
personas = st.slider("Nº Personas", 0, 100, ln["personas"])
coste_personal = st.slider("Coste Medio Personal (€)", 30000, 90000, ln["coste_medio_persona"], step=5000)
subactividad = st.slider("Subactividad (%)", 0, 30, param["subactividad_permitida_%"])

# Nuevo cálculo margen bruto
ingresos_simulados = tarifa * proyectos
costes_directos_simulados = (coste_personal * personas) + (ln["costes_directos_%"]/100 * ingresos_simulados)
margen_bruto_simulado = ingresos_simulados - costes_directos_simulados

st.success(f"📈 Nuevo Margen Bruto Simulado: {formato_eur(margen_bruto_simulado)} €")

# Gráfico de utilización
st.subheader("📊 Utilización del Equipo")
fig2, ax2 = plt.subplots()
ax2.barh(["Utilización"], [res['subactividad']['utilizacion_real_%']], color="#144C44")
ax2.axvline(benchmark['utilizacion_%'], color="#fb9200", linestyle='--', label='Benchmark')
ax2.set_xlim(0, 100)
ax2.set_xlabel("%")
ax2.legend()
st.pyplot(fig2)

# Gráfico ingresos/costes/margen
st.subheader("📊 Ingresos vs Costes Directos vs Margen Bruto")
fig3, ax3 = plt.subplots()
ax3.bar(["Ingresos", "Costes Directos", "Margen Bruto"],
        [ingresos_simulados, costes_directos_simulados, margen_bruto_simulado],
        color=["#144C44", "#fb9200", "#144C44"])
for i, val in enumerate([ingresos_simulados, costes_directos_simulados, margen_bruto_simulado]):
    ax3.text(i, val, formato_eur(val), ha='center', va='bottom', fontsize=10)
st.pyplot(fig3)
