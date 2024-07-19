import pandas as pd
import gspread
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
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

print(private_key)

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
st.markdown('<h1 class="title">Dashboard Insights</h1>', unsafe_allow_html=True)

iframe = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%;">
<iframe width="900" height="530" src="https://lookerstudio.google.com/embed/reporting/f31cd527-df04-429a-8c4a-f5f32882d4ee/page/p_wa0b5m3tid" frameborder="0" style="border:0" allowfullscreen sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
</div>
""" 

components.html(iframe, height=540)