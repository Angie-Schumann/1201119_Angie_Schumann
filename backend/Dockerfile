# =============================================================
# DOCKERFILE - BACKEND FLASK
# Construye la imagen del servidor Python que expone la API REST
# =============================================================

# Imagen base oficial de Python 3.11 version "slim" (mas liviana, sin extras)
FROM python:3.11-slim

# Define el directorio de trabajo dentro del contenedor
# Todos los comandos siguientes se ejecutan desde /app
WORKDIR /app

# Copia primero solo el archivo de dependencias
# Esto aprovecha el cache de Docker: si requirements.txt no cambia,
# Docker no vuelve a instalar las librerias en cada build
COPY requirements.txt .

# Instala las dependencias de Python
# --no-cache-dir: no guarda cache de pip (reduce el tamano de la imagen)
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del codigo fuente al contenedor
COPY . .

# Documenta que el contenedor escucha en el puerto 5000
# (No abre el puerto, eso lo hace docker-compose)
EXPOSE 5000

# Comando que se ejecuta al iniciar el contenedor
# Corre Flask directamente (en produccion usariamos gunicorn)
CMD ["python", "app.py"]
