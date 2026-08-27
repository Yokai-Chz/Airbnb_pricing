# 1. Usar imagen slim (Ahorro de ~800MB)
FROM python:3.10-slim

WORKDIR /app

# 2. Instalar compiladores, pero SIN paquetes recomendados extra (--no-install-recommends)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* # Limpiar caché de apt

# 3. Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. TRUCO DE OPTIMIZACIÓN: Desinstalar los compiladores de C++ que ya no necesitamos
RUN apt-get purge -y --auto-remove build-essential

# 5. Copiar el código
COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]