import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

import matplotlib.pyplot as plt
from scipy.stats import expon

st.set_page_config(
    page_title="Simulación Gasolinera Shell",
    page_icon="⛽",
    layout="wide"
)

st.title("Gasolinera Shell — Análisis para Simulación")
st.markdown("Carga el archivo Excel estandarizado para obtener los parámetros del modelo en Simio.")

archivo = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

if archivo:
    st.success(f"Archivo cargado: {archivo.name}")

    as_df = pd.read_excel(archivo, sheet_name="Autoservicio",      header=1)
    sc_df = pd.read_excel(archivo, sheet_name="Servicio_Completo", header=1)
    sh_df = pd.read_excel(archivo, sheet_name="Shell_Select",      header=1)

    # ── Funciones base ──
    def promedio(serie):
        datos = serie.dropna()
        datos = datos[datos > 0]
        return round(datos.mean(), 2)

    def tasa_llegada_total(df):

        tasas = []
        for bomba, grupo in df.groupby("Bomba"):
            tiempos = grupo["T. Llegada (s)"].dropna()
            tiempos = tiempos[tiempos > 0]
            if len(tiempos) > 0:
                media_bomba = tiempos.mean()
                tasas.append(1 / media_bomba)
        tasa_total = sum(tasas)
        interarrival = round(1 / tasa_total, 2)
        return interarrival

    def prueba_ks(serie):

        datos = serie.dropna()
        datos = datos[datos > 0].values
        media = datos.mean()
        stat, p_valor = stats.kstest(datos, 'expon', args=(0, media))
        return round(stat, 4), round(p_valor, 4)

    # ── Inter-arrival por sistema ──
    mu_arr_as = tasa_llegada_total(as_df)
    mu_arr_sc = tasa_llegada_total(sc_df)

    ks_as, p_as = prueba_ks(as_df["T. Llegada (s)"])
    ks_sc, p_sc = prueba_ks(sc_df["T. Llegada (s)"])

    # ── Pago PATS ──
    mu_pago = promedio(as_df["T. Pago PATS (s)"])

    # ── Bombeo AS por tipo de vehículo ──
    tipos = ["moto", "sedan", "camioneta", "pick_up"]
    bombeo_as = {}
    for tipo in tipos:
        filtro = as_df[as_df["Tipo Vehículo"] == tipo]["T. Bombeo (s)"]
        bombeo_as[tipo] = promedio(filtro)

    # ── Tiempo total SC por tipo de vehículo ──
    tiempo_sc = {}
    for tipo in tipos:
        filtro = sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Total Servicio (s)"]
        tiempo_sc[tipo] = promedio(filtro)

    # ── Shell Select ──
    mu_shell = promedio(sh_df["T. Estancia (s)"])

    # ── Proporciones de tipo de vehículo ──
    prop_as = (as_df["Tipo Vehículo"].value_counts(normalize=True) * 100).round(1)
    prop_sc = (sc_df["Tipo Vehículo"].value_counts(normalize=True) * 100).round(1)

    # ── Mostrar resultados ──
    st.divider()
    st.subheader("Parámetros para Simio")
    st.caption("Todos los tiempos en segundos · Expresión Simio: Random.Exponential(promedio)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Autoservicio — Llegadas**")
        tabla_arr_as = pd.DataFrame([
            ["Inter-arrival AS", mu_arr_as, f"Random.Exponential({mu_arr_as})"],
        ], columns=["Variable", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_arr_as, hide_index=True, use_container_width=True)

        st.markdown("**Autoservicio — Pago**")
        tabla_as = pd.DataFrame([
            ["Tiempo Pago PATS", mu_pago, f"Random.Exponential({mu_pago})"],
        ], columns=["Variable", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_as, hide_index=True, use_container_width=True)

        st.markdown("** Autoservicio — Bombeo por tipo de vehículo**")
        tabla_bombeo = pd.DataFrame([
            [tipo.title(), bombeo_as[tipo], f"Random.Exponential({bombeo_as[tipo]})"]
            for tipo in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_bombeo, hide_index=True, use_container_width=True)

        st.markdown("**Shell Select**")
        tabla_sh = pd.DataFrame([
            ["Estancia", mu_shell, f"Random.Exponential({mu_shell})"],
        ], columns=["Variable", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_sh, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("**Servicio Completo — Llegadas**")
        tabla_arr_sc = pd.DataFrame([
            ["Inter-arrival SC", mu_arr_sc, f"Random.Exponential({mu_arr_sc})"],
        ], columns=["Variable", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_arr_sc, hide_index=True, use_container_width=True)


        st.markdown("**Servicio Completo — Tiempo total por tipo de vehículo**")
        tabla_sc = pd.DataFrame([
            [tipo.title(), tiempo_sc[tipo], f"Random.Exponential({tiempo_sc[tipo]})"]
            for tipo in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"])
        st.dataframe(tabla_sc, hide_index=True, use_container_width=True)

        st.markdown("**Probabilidades de tipo de vehículo — AS**")
        tabla_prop_as = pd.DataFrame({
            "Tipo":             prop_as.index,
            "Probabilidad (%)": prop_as.values
        })
        st.dataframe(tabla_prop_as, hide_index=True, use_container_width=True)

        st.markdown("**Probabilidades de tipo de vehículo — SC**")
        tabla_prop_sc = pd.DataFrame({
            "Tipo":             prop_sc.index,
            "Probabilidad (%)": prop_sc.values
        })
        st.dataframe(tabla_prop_sc, hide_index=True, use_container_width=True)

        st.divider()
    if st.button("Ver gráficas de distribuciones"):

        def grafica_hist(ax, datos, media, titulo, color):
            """
            Dibuja el histograma de los datos reales
            y encima la curva exponencial teórica con la media calculada.
            Así puedes ver visualmente qué tan bien se ajusta.
            """
            datos = datos.dropna()
            datos = datos[datos > 0].values
            ax.hist(datos, bins=10, density=True,
                    alpha=0.6, color=color, edgecolor='white')
            x = np.linspace(0, datos.max() * 1.2, 300)
            ax.plot(x, expon.pdf(x, scale=media),
                    color=color, linewidth=2)
            ax.set_title(titulo, fontsize=10, fontweight='bold')
            ax.set_xlabel("Segundos", fontsize=8)
            ax.set_ylabel("Densidad", fontsize=8)
            ax.text(0.97, 0.95, f'Media = {media}s',
                    transform=ax.transAxes, ha='right', va='top',
                    fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        COLOR_AS    = '#7F77DD'
        COLOR_SC    = '#1D9E75'
        COLOR_SHELL = '#D85A30'

        st.markdown("**Llegadas y tiempos generales**")
        fig1, axes1 = plt.subplots(1, 3, figsize=(14, 4))
        fig1.patch.set_facecolor('#FAFAFA')

        grafica_hist(axes1[0], as_df["T. Llegada (s)"],
                     mu_arr_as, "Inter-arrival — Autoservicio", COLOR_AS)
        grafica_hist(axes1[1], sc_df["T. Llegada (s)"],
                     mu_arr_sc, "Inter-arrival — Servicio Completo", COLOR_SC)
        grafica_hist(axes1[2], sh_df["T. Estancia (s)"],
                     mu_shell, "Shell Select — Estancia", COLOR_SHELL)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()

        st.markdown("**Autoservicio — Bombeo por tipo de vehículo**")
        fig2, axes2 = plt.subplots(1, 4, figsize=(14, 4))
        fig2.patch.set_facecolor('#FAFAFA')

        for idx, tipo in enumerate(tipos):
            datos_tipo = as_df[as_df["Tipo Vehículo"] == tipo]["T. Bombeo (s)"]
            grafica_hist(axes2[idx], datos_tipo,
                         bombeo_as[tipo], f"Bombeo AS — {tipo.title()}", COLOR_AS)

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        st.markdown("**Servicio Completo — Tiempo total por tipo de vehículo**")
        fig3, axes3 = plt.subplots(1, 4, figsize=(14, 4))
        fig3.patch.set_facecolor('#FAFAFA')

        for idx, tipo in enumerate(tipos):
            datos_tipo = sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Total Servicio (s)"]
            grafica_hist(axes3[idx], datos_tipo,
                         tiempo_sc[tipo], f"SC — {tipo.title()}", COLOR_SC)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

else:
    st.info("Sube el archivo Excel para comenzar.")