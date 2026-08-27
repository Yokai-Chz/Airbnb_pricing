import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cotizador Airbnb CDMX", layout="wide")

@st.cache_data
def load_market_data():
    try:
        # Lee el dataset original de la carpeta que copiamos
        df = pd.read_csv("data/listings.csv") # Cambia a listings.csv.gz si usas el comprimido
        
        # Limpieza rápida en memoria
        df = df.dropna(subset=['price'])
        df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
        
        # Filtramos outliers para que la gráfica sea legible
        limite_superior = df['price'].quantile(0.95)
        df = df[(df['price'] >= 150) & (df['price'] <= limite_superior)]
        
        return df[['neighbourhood_cleansed', 'price']]
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame(columns=["neighbourhood_cleansed", "price"])

df_market = load_market_data()

st.title("Airbnb pricing (CDMX)")
st.write("Ajusta las características físicas de la propiedad para obtener una sugerencia de precio basada en el mercado actual.")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Ubicación y Tipo")
    neighbourhood = st.selectbox("Alcaldía", [
        "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán", 
        "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco", 
        "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta", 
        "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco"
    ])
    
    traduccion_cuarto = {
        "Casa/Depto entero": "Entire home/apt",
        "Habitación privada": "Private room",
        "Habitación compartida": "Shared room"
    }
    room_type_es = st.selectbox("Tipo de Alojamiento", list(traduccion_cuarto.keys()))
    
    # Coordenadas base (CDMX)
    latitude = 19.4270
    longitude = -99.1676
    
    # Validación: Mínimo 1, forzado a ser entero (step=1)
    minimum_nights = st.number_input("Noches Mínimas de Reserva", min_value=1, max_value=365, value=1, step=1)

with col2:
    st.subheader("Capacidad y Distribución")
    
    # Validación: Máximo 16 huéspedes
    accommodates = st.number_input("Huéspedes máximos", min_value=1, max_value=16, value=2, step=1)
    
    # Validación: Máximo 15 habitaciones
    bedrooms = st.number_input("Habitaciones (0 = Estudio)", min_value=0, max_value=15, value=1, step=1)
    
    # Validación: Máximo 20 camas
    beds = st.number_input("Camas", min_value=1, max_value=20, value=1, step=1)
    
    # Validación: Máximo 15 baños
    bathrooms = st.number_input("Baños (Permite 0.5)", min_value=0.0, max_value=15.0, value=1.0, step=0.5)

with col3:
    st.subheader("Amenidades")
    st.write("Selecciona los servicios disponibles:")
    has_wifi = st.toggle("WiFi", value=True)
    has_parking = st.toggle("Estacionamiento", value=False)
    has_ac = st.toggle("Aire Acondicionado", value=False)
    has_pool = st.toggle("Alberca / Piscina", value=False)

st.markdown("---")

if st.button("Calcular Precio Dinámico", type="primary", use_container_width=True):
    
    payload = {
        "neighbourhood_cleansed": neighbourhood,
        "room_type": traduccion_cuarto[room_type_es], 
        "latitude": latitude,
        "longitude": longitude,
        "accommodates": accommodates,
        "bathrooms": float(bathrooms),
        "bedrooms": float(bedrooms),
        "beds": float(beds),
        "minimum_nights": minimum_nights,
        "has_pool": 1 if has_pool else 0,
        "has_ac": 1 if has_ac else 0,
        "has_parking": 1 if has_parking else 0,
        "has_wifi": 1 if has_wifi else 0
    }

    API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
    
    try:
        with st.spinner('Evaluando propiedad y analizando mercado...'):
            response = requests.post(API_URL, json=payload)
            
        if response.status_code == 200:
            data = response.json()
            precio = data["suggested_price_mxn"]
            st.success(f"### Precio Sugerido de Salida: ${precio:,.2f} MXN / noche")
            
            # ==========================================
            # ESTA ES LA SECCIÓN QUE FALTABA
            # ==========================================
            st.markdown("---")
            st.subheader("Análisis de Mercado en la Zona")
            
            if not df_market.empty:
                df_zona = df_market[df_market["neighbourhood_cleansed"] == neighbourhood]
                
                if not df_zona.empty:
                    # 1. KPIs de la Zona
                    precio_promedio = df_zona["price"].mean()
                    precio_mediano = df_zona["price"].median()
                    oferta_activa = len(df_zona)
                    
                    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                    col_kpi1.metric("Precio Promedio (Zona)", f"${precio_promedio:,.2f} MXN")
                    col_kpi2.metric("Precio Mediano (Zona)", f"${precio_mediano:,.2f} MXN")
                    col_kpi3.metric("Propiedades Competidoras", f"{oferta_activa:,}")
                    
                    # 2. Gráfico de Distribución con Plotly
                    fig = px.histogram(
                        df_zona, 
                        x="price", 
                        nbins=40,
                        title=f"Distribución de Precios Actuales en {neighbourhood}",
                        labels={"price": "Precio por Noche (MXN)", "count": "Cantidad de Propiedades"},
                        color_discrete_sequence=["#1f77b4"]
                    )
                    
                    # Línea roja indicando dónde se ubica la propiedad cotizada
                    fig.add_vline(
                        x=precio, 
                        line_dash="dash", 
                        line_color="red", 
                        annotation_text="Tu Precio Sugerido",
                        annotation_position="top right"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay suficientes datos históricos para esta alcaldía.")
            else:
                st.warning("El dataset de mercado no se cargó correctamente.")
                
        else:
            st.error(f"Error en la API (Código {response.status_code}).")
            st.json(response.json())
            
    except requests.exceptions.ConnectionError:
        st.error("Error crítico: No se pudo conectar con el Backend.")