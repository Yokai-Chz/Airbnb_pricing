# Usar imagen ligera de Python
FROM python:3.10-slim

WORKDIR /app

# Instalar las librerías necesarias para la vista
RUN pip install --no-cache-dir streamlit requests

# Copiar el código del frontend
COPY app.py .

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para iniciar la aplicación web
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]