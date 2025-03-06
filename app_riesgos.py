from codigo_de_ejecucion import *
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title='DS4B Risk Score Analyzer',
     page_icon='DS4B_Logo_Blanco_Vertical_FB.png',
     layout='wide')

# SIDEBAR
with st.sidebar:
    st.image('risk_score.jpg')

    # INPUTS DE LA APLICACION
    principal = st.number_input('Importe Solicitado', 500, 50000)
    finalidad = st.selectbox('Finalidad Préstamo', ['debt_consolidation', 'credit_card', 'home_improvement', 'other'])
    num_cuotas = st.radio('Número Cuotas', ['36 months', '60 months'])
    ingresos = st.slider('Ingresos anuales', 20000, 300000)

    # DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    ingresos_verificados = 'Verified'
    antigüedad_empleo = '10+ years'
    rating = 'B'
    dti = 28
    num_lineas_credito = 3
    porc_uso_revolving = 50
    tipo_interes = 7.26
    imp_cuota = 500
    num_derogatorios = 0
    vivienda = 'MORTGAGE'

# MAIN
st.title('DS4B RISK SCORE ANALYZER')

# CALCULAR
if st.sidebar.button('CALCULAR RIESGO'):
    # Crear el registro
    registro = pd.DataFrame({'ingresos_verificados': ingresos_verificados,
                             'vivienda': vivienda,
                             'finalidad': finalidad,
                             'num_cuotas': num_cuotas,
                             'antigüedad_empleo': antigüedad_empleo,
                             'rating': rating,
                             'ingresos': ingresos,
                             'dti': dti,
                             'num_lineas_credito': num_lineas_credito,
                             'porc_uso_revolving': porc_uso_revolving,
                             'principal': principal,
                             'tipo_interes': tipo_interes,
                             'imp_cuota': imp_cuota,
                             'num_derogatorios': num_derogatorios},
                            index=[0])

    # Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    # Extraer valores
    kpi_pd = float(EL.pd.iloc[0] * 100)
    kpi_ead = float(EL.ead.iloc[0] * 100)
    kpi_lgd = float(EL.lgd.iloc[0] * 100)
    kpi_el = float(EL.principal.iloc[0] * EL.pd.iloc[0] * EL.ead.iloc[0] * EL.lgd.iloc[0])

    # Función para crear velocímetros
    def plot_gauge(value, title):
        fig, ax = plt.subplots()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        theta = np.linspace(-np.pi, 0, 100)
        ax.plot(np.cos(theta), np.sin(theta), color='black', lw=2)
        ax.fill_betweenx(np.sin(theta), 0, np.cos(theta), where=(np.cos(theta) <= np.cos(np.pi * value / 100)), color='red')
        ax.text(0, -0.5, f'{value:.2f}%', fontsize=12, ha='center')
        ax.text(0, 0.8, title, fontsize=14, ha='center', fontweight='bold')
        ax.axis('off')
        return fig

    # Mostrar gráficos
    col1, col2, col3 = st.columns(3)
    with col1:
        st.pyplot(plot_gauge(kpi_pd, "PD"))
    with col2:
        st.pyplot(plot_gauge(kpi_ead, "EAD"))
    with col3:
        st.pyplot(plot_gauge(kpi_lgd, "LGD"))

    # Prescripción
    col1, col2 = st.columns(2)
    with col1:
        st.write('La pérdida esperada es de (Euros):')
        st.metric(label="PÉRDIDA ESPERADA", value=f"{kpi_el:,.2f}")
    with col2:
        st.write('Se recomienda un extratipo de (Euros):')
        st.metric(label="COMISIÓN A APLICAR", value=f"{kpi_el * 3:,.2f}")
else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')
