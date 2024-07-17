# Configuration Instructions

This project uses different configurations for development and production environments.
The environment is determined by the `ENVIRONMENT` variable, which can be set to `dev` or `prod`.

## Setting up the Environment

1. Create a `.env` file in the root of your project with the following content:

ENVIRONMENT=dev

2. In development, configurations are loaded from a `config.toml` file. 
   Example `config.toml`:

google_sheet_id = "your_google_sheet_id"
nombre_google_sheet_hoja = "your_google_sheet_sheet_name"
type = "your_type"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "your_private_key"
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "your_auth_uri"
token_uri = "your_token_uri"
auth_provider_x509_cert_url = "your_auth_provider_x509_cert_url"
client_x509_cert_url = "your_client_x509_cert_url"
universe_domain = "your_universe_domain"

3. In production, configurations are loaded from `st.secrets`.
   Make sure to set these secrets in your Streamlit sharing app.