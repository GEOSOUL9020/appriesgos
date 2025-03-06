from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts

#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'DS4B Risk Score Analyzer',
     page_icon = 'DS4B_Logo_Blanco_Vertical_FB.png',
     layout = 'wide')

#SIDEBAR
with st.sidebar:
    st.image('risk_score.jpg')

    #INPUTS DE LA APLICACION
    principal = st.number_input('Importe Solicitado', 500, 50000)
    finalidad = st.selectbox('Finalidad Préstamo', ['debt_consolidation','credit_card','home_improvement','other'])
    num_cuotas = st.radio('Número Cuotas', ['36 months','60 months'])
    ingresos = st.slider('Ingresos anuales', 20000, 300000)

    #DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
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




#MAIN
st.title('DS4B RISK SCORE ANALYZER')


#CALCULAR

#Crear el registro
registro = pd.DataFrame({'ingresos_verificados':ingresos_verificados,
                         'vivienda':vivienda,
                         'finalidad':finalidad,
                         'num_cuotas':num_cuotas,
                         'antigüedad_empleo':antigüedad_empleo,
                         'rating':rating,
                         'ingresos':ingresos,
                         'dti':dti,
                         'num_lineas_credito':num_lineas_credito,
                         'porc_uso_revolving':porc_uso_revolving,
                         'principal':principal,
                         'tipo_interes':tipo_interes,
                         'imp_cuota':imp_cuota,
                         'num_derogatorios':num_derogatorios}
                        ,index=[0])



# CALCULAR RIESGO
if st.sidebar.button('CALCULAR RIESGO'):
    # Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    # Asegurarse de que estamos extrayendo un número correcto de los modelos
    kpi_pd = float(EL.pd.iloc[0] * 100)  # Convertir a float extrayendo el primer valor de la serie
    kpi_ead = float(EL.ead.iloc[0] * 100)  # Convertir a float
    kpi_lgd = float(EL.lgd.iloc[0] * 100)  # Convertir a float
    kpi_el = float(EL.principal.iloc[0] * EL.pd.iloc[0] * EL.ead.iloc[0] * EL.lgd.iloc[0])

    # Verificar el tipo de cada variable antes de pasarlas al gráfico
    st.write(f'kpi_pd (tipo: {type(kpi_pd)}): {kpi_pd}')
    st.write(f'kpi_ead (tipo: {type(kpi_ead)}): {kpi_ead}')
    st.write(f'kpi_lgd (tipo: {type(kpi_lgd)}): {kpi_lgd}')
    st.write(f'kpi_el (tipo: {type(kpi_el)}): {kpi_el}')

    # Velocímetros
    pd_options = {
        "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
        "series": [
            {
                "name": "PD",
                "type": "gauge",
                "axisLine": {
                    "lineStyle": {
                        "width": 10,
                    },
                },
                "progress": {"show": "true", "width": 10},
                "detail": {"valueAnimation": "true", "formatter": "{value}"},
                "data": [{"value": kpi_pd, "name": "PD"}],
            }
        ],
    }

    # Velocímetro para ead
    ead_options = {
        "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
        "series": [
            {
                "name": "EAD",
                "type": "gauge",
                "axisLine": {
                    "lineStyle": {
                        "width": 10,
                    },
                },
                "progress": {"show": "true", "width": 10},
                "detail": {"valueAnimation": "true", "formatter": "{value}"},
                "data": [{"value": kpi_ead, "name": "EAD"}],
            }
        ],
    }

    # Velocímetro para lgd
    lgd_options = {
        "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
        "series": [
            {
                "name": "LGD",
                "type": "gauge",
                "axisLine": {
                    "lineStyle": {
                        "width": 10,
                    },
                },
                "progress": {"show": "true", "width": 10},
                "detail": {"valueAnimation": "true", "formatter": "{value}"},
                "data": [{"value": kpi_lgd, "name": "LGD"}],
            }
        ],
    }

    # Representarlos en la app
    col1, col2, col3 = st.columns(3)
    with col1:
        st_echarts(options=pd_options, width="110%", key=0)
    with col2:
        st_echarts(options=ead_options, width="110%", key=1)
    with col3:
        st_echarts(options=lgd_options, width="110%", key=2)

    # Prescripción
    col1, col2 = st.columns(2)
    with col1:
        st.write('La pérdida esperada es de (Euros):')
        st.metric(label="PÉRDIDA ESPERADA", value=kpi_el)
    with col2:
        st.write('Se recomienda un extratipo de (Euros):')
        st.metric(label="COMISIÓN A APLICAR", value=kpi_el * 3)  # Metido en estático por simplicidad
else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')



