import streamlit as st
import pandas as pd

# ── Configuración de la página ──
st.set_page_config(
    page_title="Simulación Gasolinera Shell",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Gasolinera Shell — Análisis para Simulación")
st.markdown("Carga el archivo Excel estandarizado para obtener los parámetros del modelo en Simio.")

# ── Carga del archivo ──
archivo = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

if archivo:
    st.success(f"Archivo cargado: {archivo.name}")
    
    # Leer las hojas
    as_df   = pd.read_excel(archivo, sheet_name="Autoservicio")
    sc_df   = pd.read_excel(archivo, sheet_name="Servicio_Completo")
    sh_df   = pd.read_excel(archivo, sheet_name="Shell_Select")
    cfg_df  = pd.read_excel(archivo, sheet_name="Configuracion")

    st.write("### Vista previa — Autoservicio")
    st.dataframe(as_df)

    st.write("### Vista previa — Servicio Completo")
    st.dataframe(sc_df)

    st.write("### Vista previa — Shell Select")
    st.dataframe(sh_df)
else:
    st.info("Sube el archivo Excel para comenzar.")