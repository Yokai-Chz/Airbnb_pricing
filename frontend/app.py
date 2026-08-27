import streamlit as st
import requests, os


st.set_page_config(page_title="Cotizador Airbnb CDMX", layout="wide")

st.title("Estimador de Precios Dinámicos para Airbnb (CDMX)")
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
        with st.spinner('Evaluando propiedad...'):
            response = requests.post(API_URL, json=payload)
            
        if response.status_code == 200:
            data = response.json()
            precio = data["suggested_price_mxn"]
            st.success(f"### Precio Sugerido de Salida: ${precio:,.2f} MXN / noche")
        else:
            st.error(f"Error en la API (Código {response.status_code}).")
            st.json(response.json())
            
    except requests.exceptions.ConnectionError:
        st.error("Error crítico: No se pudo conectar con el Backend.")