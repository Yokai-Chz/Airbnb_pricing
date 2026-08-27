from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import joblib
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# --- CONFIGURACIÓN DE BD ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secretpassword@db:5432/airbnb_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_data = Column(Text)
    predicted_price = Column(Float)

Base.metadata.create_all(bind=engine)

# --- INICIALIZACIÓN ---
app = FastAPI(title="Airbnb Dynamic Pricing API - Modelo Hedónico")

try:
    model = joblib.load("models/airbnb_pricing_pipeline.pkl")
except Exception as e:
    model = None
    print(f"Error cargando el modelo: {e}")

# Esquema puramente físico
class AirbnbListing(BaseModel):
    neighbourhood_cleansed: str
    room_type: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    
    # Validaciones de negocio inmobiliario con máximos lógicos
    accommodates: int = Field(..., ge=1, le=16, description="Límite estándar de Airbnb (1-16).")
    bathrooms: float = Field(..., ge=0.0, le=15.0, description="Máximo 15 baños.")
    bedrooms: int = Field(..., ge=0, le=15, description="Máximo 15 habitaciones.")
    beds: int = Field(..., ge=1, le=20, description="Máximo 20 camas.")
    minimum_nights: int = Field(..., ge=1, le=365, description="Máximo 1 año.")
    
    # Amenidades estrictamente binarias
    has_pool: int = Field(..., ge=0, le=1)
    has_ac: int = Field(..., ge=0, le=1)
    has_parking: int = Field(..., ge=0, le=1)
    has_wifi: int = Field(..., ge=0, le=1)
# --- ENDPOINT ---
@app.post("/predict")
def predict_price(listing: AirbnbListing):
    if model is None:
        raise HTTPException(status_code=500, detail="El modelo no está disponible.")
    
    try:
        input_dict = listing.model_dump()
        input_data = pd.DataFrame([input_dict])
        
        prediccion = model.predict(input_data)
        precio_estimado = round(float(prediccion[0]), 2)
        
        db = SessionLocal()
        nuevo_registro = PredictionLog(
            input_data=json.dumps(input_dict),
            predicted_price=precio_estimado
        )
        db.add(nuevo_registro)
        db.commit()
        db.close()
        
        return {
            "status": "success",
            "suggested_price_mxn": precio_estimado
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en predicción: {str(e)}")