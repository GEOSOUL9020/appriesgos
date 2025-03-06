from codigo_de_ejecucion import *
import streamlit as st
import pandas as pd

# CONFIGURACION DE LA PÁGINA
st.set_page_config(
    page_title='DS4B Risk Score Analyzer',
    page_icon='DS4B_Logo_Blanco_Vertical_FB.png',
    layout='wide'
)

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
# Crear el registro
registro = pd.DataFrame({
    'ingresos_verificados': ingresos_verificados,
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
    'num_derogatorios': num_derogatorios
}, index=[0])

# CALCULAR RIESGO
if st.sidebar.button('CALCULAR RIESGO'):
    # Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    # Calcular los kpis y redondearlos a enteros
    kpi_pd = round(float(EL.pd * 100))
    kpi_ead = round(float(EL.ead * 100))
    kpi_lgd = round(float(EL.lgd * 100))
    kpi_el = round(float(EL.principal * EL.pd * EL.ead * EL.lgd))

    # Generar el código HTML y JavaScript para los velocímetros
    def generate_gauge_html(kpi, name):
        width = 260  # Aumenta el ancho un 30% (200 * 1.3)
        height = 195 # Aumenta la altura un 30% (150 * 1.3)
        html = f"""
        <div id="{name}-gauge" style="width: {width}px; height: {height}px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <script type="text/javascript">
            var chart = echarts.init(document.getElementById('{name}-gauge'));
            var option = {{
                tooltip: {{formatter: '{{a}} <br/>{{b}} : {{c}}%'}},
                series: [{{
                    name: '{name}',
                    type: 'gauge',
                    axisLine: {{lineStyle: {{width: 10}}}},
                    progress: {{show: true, width: 10}},
                    detail: {{valueAnimation: true, formatter: '{{value}}'}},
                    data: [{{value: {kpi}, name: '{name}'}}]
                }}]
            }};
            chart.setOption(option);
        </script>
        """
        return html

    # Representarlos en la app
    col1, col2, col3 = st.columns(3)
    with col1:
        st.components.v1.html(generate_gauge_html(kpi_pd, 'PD'), width=260, height=195)
    with col2:
        st.components.v1.html(generate_gauge_html(kpi_ead, 'EAD'), width=260, height=195)
    with col3:
        st.components.v1.html(generate_gauge_html(kpi_lgd, 'LGD'), width=260, height=195)

    # Prescripción
    col1, col2 = st.columns(2)
    with col1:
        st.write('La pérdida esperada es de (Euros):')
        st.metric(label="PÉRDIDA ESPERADA", value=kpi_el)
    with col2:
        st.write('Se recomienda un extratipo de (Euros):')
        st.metric(label="COMISIÓN A APLICAR", value=round(kpi_el * 3))
else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')
