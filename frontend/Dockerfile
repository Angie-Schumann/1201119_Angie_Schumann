# =============================================================
# DOCKERFILE - FRONTEND VUE.JS
# Usa un build multi-etapa (multi-stage build):
# Etapa 1 (builder): Compila la aplicacion Vue con Node.js
# Etapa 2 (produccion): Sirve los archivos con Nginx (mas ligero)
# Este patron reduce el tamano final de la imagen drasticamente
# =============================================================

# ---------- ETAPA 1: COMPILACION ----------
# Imagen base de Node.js para compilar la aplicacion Vue
FROM node:20-alpine AS builder

# Directorio de trabajo en el contenedor de compilacion
WORKDIR /app

# Copia los archivos de dependencias primero
# (aprovecha el cache de Docker: si no cambian, no reinstala)
COPY package*.json ./

# Instala todas las dependencias del proyecto Vue (devDependencies incluidas)
RUN npm install

# Copia el resto del codigo fuente
COPY . .

# Define la variable de entorno para que Vite la incluya en el build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Compila la aplicacion Vue para produccion
# Genera archivos estaticos optimizados en la carpeta /app/dist
RUN npm run build


# ---------- ETAPA 2: SERVIDOR WEB ----------
# Imagen oficial de Nginx, version alpine (muy liviana ~20MB)
FROM nginx:alpine

# Elimina la configuracion por defecto de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia nuestra configuracion personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia los archivos compilados de Vue (de la etapa anterior)
# al directorio donde Nginx sirve los archivos estaticos
COPY --from=builder /app/dist /usr/share/nginx/html

# Documenta que el contenedor escucha en el puerto 80
EXPOSE 80

# Inicia Nginx en primer plano (necesario para Docker)
CMD ["nginx", "-g", "daemon off;"]
