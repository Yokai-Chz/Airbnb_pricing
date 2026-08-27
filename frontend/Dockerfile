# Usar imagen ligera de Python
FROM python:3.10-slim

WORKDIR /app

# Instalar las librerías necesarias para la vista
RUN pip install --no-cache-dir streamlit requests pandas plotly

# Copiar el código del frontend
COPY frontend/app.py .

COPY data/ ./data/

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para iniciar la aplicación web
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]