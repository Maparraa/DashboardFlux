import pandas as pd
import gspread
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
import os
import toml

load_dotenv()
ENV = os.getenv('ENVIRONMENT', 'prod')

if ENV == 'dev':
    config = toml.load("config.toml")
    google_sheet_id = config['google_sheet_id_Res']
    nombre_google_sheet_hoja = config['nombre_google_sheet_hoja']
    type = config['type']
    project_id = config['project_id']
    private_key_id = config['private_key_id']
    private_key = config['private_key']
    client_email = config['client_email']
    client_id = config['client_id']
    auth_uri = config['auth_uri']
    token_uri = config['token_uri']
    auth_provider_x509_cert_url = config['auth_provider_x509_cert_url']
    client_x509_cert_url = config['client_x509_cert_url']
    universe_domain = config['universe_domain']
else:
    google_sheet_id = st.secrets["google_sheet_id_Res"] 
    nombre_google_sheet_hoja = st.secrets["nombre_google_sheet_hoja"]
    type = st.secrets["type"]
    project_id = st.secrets['project_id']
    private_key_id = st.secrets['private_key_id']
    private_key = st.secrets['private_key']
    client_email = st.secrets['client_email']
    client_id = st.secrets['client_id']
    auth_uri = st.secrets['auth_uri']
    token_uri = st.secrets['token_uri']
    auth_provider_x509_cert_url = st.secrets['auth_provider_x509_cert_url']
    client_x509_cert_url = st.secrets['client_x509_cert_url']
    universe_domain = st.secrets['universe_domain']

meta = {'Cot - Reserva': 10,'Reserva - Informe': 10,'Informe - Firma contrato': 10,'Firma contrato - Adecuaciones': 45,'Adecuaciones - Fin Instalación': 15,'Fin instalación - Ingreso TE-4': 2,'Ingreso TE-4 - TE-4 inscrito': 13,'TE-4 Inscrito - Ingreso F5': 2,'Ingreso F5 - PC (F6)': 13}

client = dict({
    'type': type,
    'project_id': project_id,
    'private_key_id': private_key_id,
    'private_key': private_key,
    'client_email': client_email,
    'client_id': client_id,
    'auth_uri': auth_uri,
    'token_uri': token_uri,
    'auth_provider_x509_cert_url': auth_provider_x509_cert_url,
    'client_x509_cert_url': client_x509_cert_url,
    'universe_domain': universe_domain
})

gc = gspread.service_account_from_dict(client)
spreadsheet = gc.open_by_key(google_sheet_id)
worksheet = spreadsheet.worksheet(nombre_google_sheet_hoja)

# Obtener datos de Google Sheets
data = worksheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df = df[df['Año cotización'] != '']
df_transformado = pd.melt(df, id_vars=['Ceco', 'Año cotización'], var_name='Tiempo', value_name='Valor')
df_transformado = df_transformado[pd.to_numeric(df_transformado['Valor'], errors='coerce').notnull()]
df_transformado['Valor'] = df_transformado['Valor'].str.replace('.', '').str.replace(',', '.').astype(float)

# Convertir la columna "Tiempo" a un tipo categórico con un orden específico
df_transformado['Tiempo'] = pd.Categorical(df_transformado['Tiempo'], categories=data[0][2:], ordered=True)
list_year_cotizacion = df_transformado['Año cotización'].unique().copy()
list_year_cotizacion.sort()

st.set_page_config(page_title="Dashboard Flux", page_icon="☀", layout="wide")

# Título de la aplicación
st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 class="title">Boxplot etapas Residencial</h1>', unsafe_allow_html=True)

# Checklist para seleccionar portfolios
selected_years = st.multiselect(
    'Selecciona Año cotización',
    options=list_year_cotizacion,
    default=['2024']
)

# Dropdown para seleccionar CeCos
selected_cecos = st.multiselect(
    'Selecciona CeCo...',
    options= df_transformado[df_transformado['Año cotización'].isin(selected_years)]['Ceco'].unique()
)

outliers_y_n = st.checkbox(
    'Desea ver los outliers',
    value= False
)

all_points = st.checkbox(
    'Desea ver todos los proyectos con puntos en el gráfico',
    value= False
)

if(all_points):
    puntos = 'all'
else:
    if(outliers_y_n):
        puntos = 'outliers'
    else:
        puntos = False

# Filtrar datos según la selección de portfolios
mask = df_transformado[df_transformado['Año cotización'].isin(selected_years)]
tiempos = mask['Tiempo'].unique()
meta_filtrada = {k: meta[k] for k in tiempos if k in meta}
metas_filtradas = list(meta_filtrada.values())
max_y = mask['Valor'].max()
range_y = [0, max_y + 15] if max_y <= 150 else [0, 150]

# Crear el gráfico
fig = px.box(mask, x='Tiempo', y='Valor', points= puntos, hover_data=['Ceco'], color= 'Año cotización',
             color_discrete_map={'2024': '#146CFD', '2023': '#00B7D7'}, range_y=range_y, labels={'Valor': 'Días'})

#fig.update_traces(
#    marker_color='#072C54',
#    marker=dict(color='#D21611'),
#    line=dict(color='#AAADAF'),
#    fillcolor='#072C54'
#)

# Se agrega la meta en linea punteada
fig.add_trace(go.Scatter(
    x=tiempos, 
    y=metas_filtradas, 
    mode='lines+markers',
    name='Meta',
    line=dict(dash='dash', color='#3f4449') 
))

# Se cambia el color del fondo
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title={'text': "Boxplot etapas Residencial", 'x': 0.5, 'xanchor': 'center'},
    width=2000,
    height=700  
)
# Mostrar los puntos para los CeCo seleccionados
if selected_cecos:
    for ceco in selected_cecos:
        ceco_data = df_transformado[df_transformado['Ceco'] == ceco]
        fig.add_trace(go.Scatter(
                x= ceco_data['Tiempo'],
                y= ceco_data['Valor'],
                mode='markers',
                #marker=dict(color='red', size=6),
                text= ceco_data['Ceco'],
                textposition='top center',
                name=ceco,
                visible=True,
                showlegend= True
        ))

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)