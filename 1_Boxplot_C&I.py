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
    google_sheet_id = config['google_sheet_id']
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
    google_sheet_id = st.secrets["google_sheet_id"] 
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

meta = {'Gestión Comercial': 28,'RTE: Ready to Engineering': 14,'Desarrollo Ingeniería': 14,'Revisión Ingeniería': 14,'RTB: Ready to Build': 45,'Construcción': 87,'Gestión Certificación': 21,'Declaración SEC': 21,'Gestión Tramitación': 14,'Validación Planta Dx': 21,'Conexión de Planta': 21}

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
df = df[df['Portafolio'] != '']
df_transformado = pd.melt(df, id_vars=['Ceco', 'Portafolio'], var_name='Tiempo', value_name='Valor')
df_transformado = df_transformado[pd.to_numeric(df_transformado['Valor'], errors='coerce').notnull()]
df_transformado['Valor'] = df_transformado['Valor'].str.replace('.', '').str.replace(',', '.').astype(float)

# Convertir la columna "Tiempo" a un tipo categórico con un orden específico
df_transformado['Tiempo'] = pd.Categorical(df_transformado['Tiempo'], categories=data[0][2:], ordered=True)
list_portfolio = df_transformado['Portafolio'].unique().copy()
list_portfolio.sort()

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
st.markdown('<h1 class="title">Boxplot etapas C&I</h1>', unsafe_allow_html=True)

# Checklist para seleccionar portfolios
selected_portfolios = st.multiselect(
    'Selecciona Portafolios',
    options=list_portfolio,
    default=['Portafolio 3']
)

# Dropdown para seleccionar CeCos
selected_cecos = st.multiselect(
    'Selecciona CeCo...',
    options=df_transformado['Ceco'].unique()
)

# Filtrar datos según la selección de portfolios
mask = df_transformado[df_transformado['Portafolio'].isin(selected_portfolios)]
tiempos = mask['Tiempo'].unique()
meta_filtrada = {k: meta[k] for k in tiempos if k in meta}
metas_filtradas = list(meta_filtrada.values())

# Crear el gráfico
fig = px.box(mask, x='Tiempo', y='Valor', points='outliers', hover_data=['Ceco'], color= 'Portafolio',
             color_discrete_map={'Portafolio 1': '#19439B', 'Portafolio 2': '#146CFD', 'Portafolio 3': '#00B7D7'})

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
    title={'text': "Boxplot etapas C&I", 'x': 0.5, 'xanchor': 'center'},
    width=2000,
    height=700  
)
# Mostrar los puntos para los CeCo seleccionados
if selected_cecos:
    for ceco in selected_cecos:
        ceco_data = df_transformado[df_transformado['Ceco'] == ceco]
        for index, row in ceco_data.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['Tiempo']],
                y=[row['Valor']],
                mode='markers',
                marker=dict(color='red', size=6),
                text=[ceco],
                textposition='top center',
                name=ceco,
                visible=True,
                showlegend= False
            ))

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)