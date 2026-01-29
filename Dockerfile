# Imagen ligera con Python
FROM python:3.12-slim

# Evita .pyc y fuerza logs en consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias (mejor con requirements.txt)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código 
COPY . /app

# Crea el directorio donde irá la BD (se montará con volumen en compose)
RUN mkdir -p /sqlite3-db

# Puerto típico Flask
EXPOSE 5000

# Arranque (si tu app usa app.run())
CMD ["python", "app.py"]
