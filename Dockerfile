# Imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de la app
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para Flask
EXPOSE 8080

# Ejecutar la app con Gunicorn (más robusto que el server de desarrollo de Flask)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

