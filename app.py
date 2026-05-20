import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Simulación Gasolinera Shell",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Gasolinera Shell — Análisis para Simulación")
st.markdown("Carga el archivo Excel estandarizado para obtener los parámetros del modelo en Simio.")

archivo = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

if archivo:
    st.success(f"Archivo cargado: {archivo.name}")

    as_df = pd.read_excel(archivo, sheet_name="Autoservicio",      header=1)
    sc_df = pd.read_excel(archivo, sheet_name="Servicio_Completo", header=1)
    sh_df = pd.read_excel(archivo, sheet_name="Shell_Select",      header=1)

    as_df = as_df.dropna(subset=["Tipo Vehículo"])
    sc_df = sc_df.dropna(subset=["Tipo Vehículo"])

    tipos = ["moto", "sedan", "camioneta", "pick_up"]

    def promedio(serie):
        datos = serie.dropna()
        datos = datos[datos > 0]
        return round(datos.mean(), 2)

    def interarrival_general(df):
        tasas = []
        for bomba, grupo in df.groupby("Bomba"):
            tiempos = grupo["T. Llegada (s)"].dropna()
            tiempos = tiempos[tiempos > 0]
            if len(tiempos) > 0:
                tasas.append(1 / tiempos.mean())
        return round(1 / sum(tasas), 2)

    # ── Inter-arrival general ──
    mu_arr_as = interarrival_general(as_df)
    mu_arr_sc = interarrival_general(sc_df)

    # ── Probabilidades de tipo de vehículo ──
    prop_as = (as_df["Tipo Vehículo"].value_counts(normalize=True) * 100).round(1)
    prop_sc = (sc_df["Tipo Vehículo"].value_counts(normalize=True) * 100).round(1)

    # ── AS: Posicionamiento, Pago PATS y Bombeo por tipo ──
    pos_as, bombeo_as = {}, {}
    for tipo in tipos:
        filtro = as_df[as_df["Tipo Vehículo"] == tipo]
        pos_as[tipo]    = promedio(filtro["T. Posicionamiento (s)"])
        bombeo_as[tipo] = promedio(filtro["T. Bombeo (s)"])

    mu_pago_as = promedio(as_df["T. Pago PATS (s)"])

    # ── SC: Posicionamiento, Bombeo y Pago por tipo ──
    pos_sc, bombeo_sc, pago_sc = {}, {}, {}
    for tipo in tipos:
        filtro = sc_df[sc_df["Tipo Vehículo"] == tipo]
        pos_sc[tipo]    = promedio(filtro["T. Posicionamiento (s)"])
        bombeo_sc[tipo] = promedio(filtro["T. Bombeo (s)"])
        pago_sc[tipo]   = promedio(filtro["T. Pago SC (s)"])

    mu_pago_sc = promedio(sc_df["T. Pago SC (s)"])

    # ── Shell Select ──
    mu_shell = promedio(sh_df["T. Estancia (s)"])

    # ══════════════════════════════════════════
    # MOSTRAR RESULTADOS
    # ══════════════════════════════════════════
    st.divider()
    st.subheader("Parámetros para Simio — Distribuciones Exponenciales")
    st.caption("Todos los tiempos en segundos · Expresión en Simio: Random.Exponential(promedio)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Autoservicio — Inter-arrival general**")
        st.dataframe(pd.DataFrame([
            ["Source AS", mu_arr_as, f"Random.Exponential({mu_arr_as})"]
        ], columns=["Source", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Autoservicio — Probabilidad de tipo de vehículo**")
        st.dataframe(pd.DataFrame([
            [t.title(), f"{prop_as.get(t, 0)}%"]
            for t in tipos
        ], columns=["Tipo", "Probabilidad"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Autoservicio — Posicionamiento (EAS) por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), pos_as[t], f"Random.Exponential({pos_as[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Autoservicio — Pago PATS**")
        st.dataframe(pd.DataFrame([
            ["Todos los tipos", mu_pago_as, f"Random.Exponential({mu_pago_as})"]
        ], columns=["Aplica a", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Autoservicio — Bombeo por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), bombeo_as[t], f"Random.Exponential({bombeo_as[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Shell Select — Tiempo de estancia**")
        st.dataframe(pd.DataFrame([
            ["Todos los tipos", mu_shell, f"Random.Exponential({mu_shell})"]
        ], columns=["Aplica a", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

    with col2:
        st.markdown("**Servicio Completo — Inter-arrival general**")
        st.dataframe(pd.DataFrame([
            ["Source SC", mu_arr_sc, f"Random.Exponential({mu_arr_sc})"]
        ], columns=["Source", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Servicio Completo — Probabilidad de tipo de vehículo**")
        st.dataframe(pd.DataFrame([
            [t.title(), f"{prop_sc.get(t, 0)}%"]
            for t in tipos
        ], columns=["Tipo", "Probabilidad"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Servicio Completo — Posicionamiento (ESC) por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), pos_sc[t], f"Random.Exponential({pos_sc[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Servicio Completo — Pago SC (general)**")
        st.dataframe(pd.DataFrame([
            ["Todos los tipos", mu_pago_sc, f"Random.Exponential({mu_pago_sc})"]
        ], columns=["Aplica a", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Servicio Completo — Pago SC por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), pago_sc[t], f"Random.Exponential({pago_sc[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**Servicio Completo — Bombeo por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), bombeo_sc[t], f"Random.Exponential({bombeo_sc[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

else:
    st.info("Sube el archivo Excel para comenzar.")