import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon

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
        """
        Calcula la media descartando nulos y ceros.
        Esta media es el parámetro de Random.Exponential() en Simio.
        """
        datos = serie.dropna()
        datos = datos[datos > 0]
        return round(datos.mean(), 2)

    # ── Inter-arrival por tipo ──
    ia_as, ia_sc = {}, {}
    for tipo in tipos:
        ia_as[tipo] = promedio(
            as_df[as_df["Tipo Vehículo"] == tipo]["T. Llegada (s)"]
        )
        ia_sc[tipo] = promedio(
            sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Llegada (s)"]
        )

    # ── AS: Posicionamiento, Pago y Bombeo ──
    pos_as, bombeo_as = {}, {}
    for tipo in tipos:
        filtro = as_df[as_df["Tipo Vehículo"] == tipo]
        pos_as[tipo]    = promedio(filtro["T. Posicionamiento"])
        bombeo_as[tipo] = promedio(filtro["T. Bombeo (s)"])

    mu_pago = promedio(as_df["T. Pago PATS (s)"])

    # ── SC: Tiempo total por tipo ──
    total_sc = {}
    for tipo in tipos:
        total_sc[tipo] = promedio(
            sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Total Servicio (s)"]
        )

    # ── Shell Select ──
    mu_shell = promedio(sh_df["T. Estancia (s)"])

    # ══════════════════════════════════════════
    # MOSTRAR RESULTADOS
    # ══════════════════════════════════════════
    st.divider()
    st.subheader("📊 Parámetros para Simio — Distribuciones Exponenciales")
    st.caption("Todos los tiempos en segundos · Expresión en Simio: Random.Exponential(promedio)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔵 Autoservicio — Inter-arrival por Source**")
        st.dataframe(pd.DataFrame([
            [f"{t.title()}_AS", ia_as[t], f"Random.Exponential({ia_as[t]})"]
            for t in tipos
        ], columns=["Source", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**🔵 Autoservicio — Posicionamiento en EAS por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), pos_as[t], f"Random.Exponential({pos_as[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**🔵 Autoservicio — Tiempo de Pago PATS**")
        st.dataframe(pd.DataFrame([
            ["Todos los tipos", mu_pago, f"Random.Exponential({mu_pago})"]
        ], columns=["Aplica a", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**🔵 Autoservicio — Bombeo por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), bombeo_as[t], f"Random.Exponential({bombeo_as[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**🟠 Shell Select — Tiempo de estancia**")
        st.dataframe(pd.DataFrame([
            ["Todos los tipos", mu_shell, f"Random.Exponential({mu_shell})"]
        ], columns=["Aplica a", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

    with col2:
        st.markdown("**🟢 Servicio Completo — Inter-arrival por Source**")
        st.dataframe(pd.DataFrame([
            [f"{t.title()}_SC", ia_sc[t], f"Random.Exponential({ia_sc[t]})"]
            for t in tipos
        ], columns=["Source", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

        st.markdown("**🟢 Servicio Completo — Tiempo total por tipo**")
        st.dataframe(pd.DataFrame([
            [t.title(), total_sc[t], f"Random.Exponential({total_sc[t]})"]
            for t in tipos
        ], columns=["Tipo", "Promedio (s)", "Expresión Simio"]),
        hide_index=True, use_container_width=True)

    # ══════════════════════════════════════════
    # GRÁFICAS
    # ══════════════════════════════════════════
    st.divider()
    if st.button("📈 Ver gráficas de distribuciones"):

        def grafica_hist(ax, datos, media, titulo, color):
            """
            Histograma de datos reales con curva exponencial teórica.
            Si la curva sigue bien las barras, confirma que
            Random.Exponential es la distribución correcta.
            """
            datos = datos.dropna()
            datos = datos[datos > 0].values
            if len(datos) < 2:
                ax.set_title(f"{titulo}\n(sin datos)", fontsize=9)
                return
            ax.hist(datos, bins=10, density=True,
                    alpha=0.6, color=color, edgecolor='white')
            x = np.linspace(0, datos.max() * 1.2, 300)
            ax.plot(x, expon.pdf(x, scale=media),
                    color=color, linewidth=2)
            ax.set_title(titulo, fontsize=9, fontweight='bold')
            ax.set_xlabel("Segundos", fontsize=8)
            ax.set_ylabel("Densidad", fontsize=8)
            ax.text(0.97, 0.95, f'μ = {media}s',
                    transform=ax.transAxes, ha='right', va='top',
                    fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        C_AS    = '#7F77DD'
        C_SC    = '#1D9E75'
        C_SHELL = '#D85A30'

        # Gráfica 1 — Inter-arrival por tipo
        st.markdown("**Inter-arrival por tipo de vehículo**")
        fig1, axes1 = plt.subplots(2, 4, figsize=(16, 7))
        fig1.patch.set_facecolor('#FAFAFA')
        for idx, tipo in enumerate(tipos):
            grafica_hist(axes1[0][idx],
                         as_df[as_df["Tipo Vehículo"] == tipo]["T. Llegada (s)"],
                         ia_as[tipo], f"AS — {tipo.title()}", C_AS)
            grafica_hist(axes1[1][idx],
                         sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Llegada (s)"],
                         ia_sc[tipo], f"SC — {tipo.title()}", C_SC)
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()

        # Gráfica 2 — Posicionamiento AS por tipo
        st.markdown("**Autoservicio — Posicionamiento (EAS) por tipo**")
        fig2, axes2 = plt.subplots(1, 4, figsize=(16, 4))
        fig2.patch.set_facecolor('#FAFAFA')
        for idx, tipo in enumerate(tipos):
            grafica_hist(axes2[idx],
                         as_df[as_df["Tipo Vehículo"] == tipo]["T. Posicionamiento"],
                         pos_as[tipo], f"Posic. — {tipo.title()}", C_AS)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        # Gráfica 3 — Bombeo AS por tipo
        st.markdown("**Autoservicio — Bombeo por tipo**")
        fig3, axes3 = plt.subplots(1, 4, figsize=(16, 4))
        fig3.patch.set_facecolor('#FAFAFA')
        for idx, tipo in enumerate(tipos):
            grafica_hist(axes3[idx],
                         as_df[as_df["Tipo Vehículo"] == tipo]["T. Bombeo (s)"],
                         bombeo_as[tipo], f"Bombeo — {tipo.title()}", C_AS)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

        # Gráfica 4 — Pago PATS
        st.markdown("**Autoservicio — Pago PATS**")
        fig4, axes4 = plt.subplots(1, 1, figsize=(5, 4))
        fig4.patch.set_facecolor('#FAFAFA')
        grafica_hist(axes4, as_df["T. Pago PATS (s)"],
                     mu_pago, "Pago PATS — Todos", C_AS)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

        # Gráfica 5 — Tiempo total SC por tipo
        st.markdown("**Servicio Completo — Tiempo total por tipo**")
        fig5, axes5 = plt.subplots(1, 4, figsize=(16, 4))
        fig5.patch.set_facecolor('#FAFAFA')
        for idx, tipo in enumerate(tipos):
            grafica_hist(axes5[idx],
                         sc_df[sc_df["Tipo Vehículo"] == tipo]["T. Total Servicio (s)"],
                         total_sc[tipo], f"SC — {tipo.title()}", C_SC)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

        # Gráfica 6 — Shell Select
        st.markdown("**Shell Select — Tiempo de estancia**")
        fig6, axes6 = plt.subplots(1, 1, figsize=(5, 4))
        fig6.patch.set_facecolor('#FAFAFA')
        grafica_hist(axes6, sh_df["T. Estancia (s)"],
                     mu_shell, "Shell Select", C_SHELL)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

else:
    st.info("Sube el archivo Excel para comenzar.")