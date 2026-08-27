# Airbnb Dynamic Pricing Engine (CDMX)

Una aplicación de Machine Learning Full-Stack diseñada para estimar dinámicamente el precio óptimo por noche de propiedades de Airbnb en la Ciudad de México. 

Este proyecto implementa un **Modelo de Precios Hedónicos**, evaluando el valor de un inmueble basándose estrictamente en sus características intrínsecas (ubicación, capacidad, amenidades) para resolver el problema del "arranque en frío" en propiedades nuevas sin historial de reseñas.

## Arquitectura del Proyecto

El sistema está construido bajo una arquitectura de microservicios contenerizados:

* **Frontend:** Streamlit (Interfaz web de cotización interactiva).
* **Backend:** FastAPI (API RESTful de alto rendimiento con validación estricta de esquemas vía Pydantic).
* **Base de Datos:** PostgreSQL (Almacenamiento persistente del historial de predicciones vía SQLAlchemy).
* **Machine Learning:** Pipeline de Scikit-Learn + XGBoost Regressor (con transformación logarítmica de la variable objetivo).
* **Infraestructura:** Docker & Docker Compose (Optimizado con multi-stage builds e imágenes distroless/slim para despliegue en la nube).

## Pipeline de Machine Learning

1. **Ingeniería de Datos (ETL):** Extracción de características a partir de cadenas JSON complejas (amenidades).
2. **Selección de Características:** Eliminación de métricas de reputación para enfocar el modelo en el valor inmobiliario real, permitiendo cotizar propiedades recién listadas.
3. **Modelado:** `XGBRegressor` envuelto en un `TransformedTargetRegressor` para manejar la distribución asimétrica positiva (long-tail) de los precios en MXN.
4. **Métricas de Desempeño:**
   - Margen de Error Promedio: ~30%
   - El modelo logra un equilibrio óptimo entre generalización comercial y precisión matemática.

## Estructura del Repositorio

```text
├── data/                  # Datos crudos y limpios (No versionados por peso)
├── frontend/              # Código fuente de la interfaz Streamlit
│   ├── app.py
│   └── Dockerfile
├── models/                # Modelo serializado (.pkl)
├── notebooks/             # Análisis exploratorio (EDA) y entrenamiento del modelo
├── src/                   # Código fuente de la API (FastAPI)
│   └── main.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml     # Orquestación de servicios
├── Dockerfile             # Imagen del Backend
├── requirements.txt       # Dependencias de Python
└── README.md
```

## Instrucciones de Ejecución Local

Para levantar toda la arquitectura de manera local usando Docker:

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Yokai-Chz/Airbnb_pricing.git
cd Airbnb_pricing
```

2. **Configurar Variables de Entorno:**
Crea un archivo `.env` en la raíz del proyecto con las siguientes credenciales:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=secretpassword
POSTGRES_DB=airbnb_db
DATABASE_URL=postgresql://admin:secretpassword@db:5432/airbnb_db
API_URL=http://api:8000/predict
```

3. **Construir y Ejecutar los Contenedores:**
```bash
docker-compose up --build -d
```

4. **Acceder a los Servicios:**
- Frontend (Streamlit): `http://localhost:8501`
- Backend API Docs (Swagger): `http://localhost:8000/docs`
- Base de Datos: Puerto `5432` (Accesible vía DBeaver o pgAdmin)

## Trabajo Futuro y Escalabilidad

El proyecto está diseñado con principios Cloud-Native. Los próximos pasos para un entorno de producción incluyen:
* Migrar la base de datos a **Google Cloud SQL**.
* Desplegar las imágenes optimizadas de Backend y Frontend en **Google Cloud Run** para auto-escalamiento.
* Implementar un pipeline CI/CD con GitHub Actions para reentrenar el modelo periódicamente.
