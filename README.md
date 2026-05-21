# MediTrack - Sistema de Gestion de Salud Personal

Aplicacion de microservicios para gestionar medicamentos y citas medicas.
Desarrollada con Vue.js, Flask y MongoDB, orquestada con Docker.

---

## Estructura del Proyecto

```
proyecto_medicamentos/
├── docker-compose.yml       <- Orquesta los 3 servicios
├── .env                     <- Variables sensibles (no subir a git)
├── frontend/
│   ├── Dockerfile           <- Build multi-etapa Node -> Nginx
│   ├── nginx.conf           <- Configuracion del servidor web
│   ├── index.html           <- HTML base de Vue
│   ├── vite.config.js       <- Configuracion del bundler
│   ├── package.json         <- Dependencias npm
│   └── src/
│       ├── main.js          <- Punto de entrada de Vue
│       ├── App.vue          <- Layout principal con sidebar
│       ├── router/index.js  <- Rutas de la aplicacion
│       ├── services/api.js  <- Comunicacion con el backend
│       ├── assets/styles.css<- Estilos globales
│       └── views/
│           ├── Dashboard.vue    <- Resumen / inicio
│           ├── Medicamentos.vue <- CRUD de medicamentos
│           └── Citas.vue        <- CRUD de citas medicas
├── backend/
│   ├── Dockerfile           <- Imagen Python slim
│   ├── requirements.txt     <- Dependencias pip
│   └── app.py               <- API REST con Flask + PyMongo
└── database/
    └── init.js              <- Script de inicializacion MongoDB
```

---

## Como Levantar el Proyecto

### Requisitos previos
- Docker Desktop instalado y corriendo
- Docker Compose v2+ (incluido en Docker Desktop)

### Pasos

1. Clona o descomprime el proyecto en tu maquina

2. Asegurate de estar en la carpeta raiz del proyecto:
   ```
   cd proyecto_medicamentos
   ```

3. Levanta todos los servicios con un solo comando:
   ```
   docker compose up --build
   ```
   La primera vez tarda mas porque descarga las imagenes y compila el frontend.

4. Accede a la aplicacion:
   - Frontend (app web): http://10.22.24.0 o http://localhost
   - Backend (API):      http://10.22.24.0:5510/api/health

### Para detener los servicios:
```
docker compose down
```

### Para detener Y borrar los datos de MongoDB:
```
docker compose down -v
```

---

## Puertos del Sistema

| Servicio  | Puerto Interno | Puerto Host | Acceso        |
|-----------|---------------|-------------|---------------|
| Frontend  | 80            | 80          | Publico       |
| Backend   | 5000          | 5510        | Publico       |
| MongoDB   | 27017         | Ninguno     | Solo interno  |

---

## Endpoints de la API

### Salud del sistema
```
GET  /api/health
```

### Medicamentos
```
GET    /api/medicamentos          -> Lista todos
POST   /api/medicamentos          -> Crea nuevo
PUT    /api/medicamentos/:id      -> Actualiza
DELETE /api/medicamentos/:id      -> Elimina
```

### Citas Medicas
```
GET    /api/citas                 -> Lista todas (acepta ?completada=false)
POST   /api/citas                 -> Crea nueva
PUT    /api/citas/:id             -> Actualiza / marca completada
DELETE /api/citas/:id             -> Elimina
```

---

## Verificar que todo funciona

```bash
# Ver contenedores activos (deben aparecer los 3)
docker ps

# Ver logs del backend
docker logs flask_backend

# Verificar salud del backend
curl http://10.22.24.0:5510/api/health

# Ver datos en MongoDB
docker exec -it mongo_db mongosh \
  -u admin -p "MediPass2026Secure!" \
  --authenticationDatabase admin \
  medicamentos_db \
  --eval "db.medicamentos.find().pretty()"
```

---

## Seguridad Implementada

1. **Contrasenas en .env**: Ningun password esta escrito en el codigo
2. **MongoDB no expuesto**: El puerto 27017 de MongoDB NO aparece en ports
3. **Red interna**: Los contenedores se comunican por nombre de servicio
4. **Imagenes oficiales**: mongo:6.0, python:3.11-slim, nginx:alpine, node:20-alpine
5. **Solo puertos necesarios**: Frontend (80) y Backend (5510) unicamente
6. **Cabeceras de seguridad HTTP**: Configuradas en Nginx (X-Frame-Options, etc.)
7. **Variables de entorno**: Flask SECRET_KEY y MONGO_URI nunca en el codigo

---

## Riesgos Identificados

### Riesgo 1: Exposicion de MongoDB al exterior
- Descripcion: Si se agrega "27017:27017" en ports de mongo en docker-compose.yml,
  cualquier persona en la red podria conectarse directamente a la base de datos
  sin pasar por el backend, bypasseando toda la logica de validacion y autenticacion.
- Mitigacion aplicada: MongoDB NO tiene ports definidos en docker-compose.yml.
  Solo es accesible desde dentro de la red med_network.

### Riesgo 2: Credenciales en el codigo fuente
- Descripcion: Si las contrasenas se escriben directamente en app.py o docker-compose.yml
  y se sube el codigo a GitHub, las credenciales quedan expuestas publicamente.
- Mitigacion aplicada: Todas las credenciales estan en .env que se agrega al .gitignore.

### Riesgo 3: Contrasena debil en MongoDB
- Descripcion: La contrasena por defecto del proyecto es funcional pero debe cambiarse
  antes de llevar esto a produccion real.
- Mitigacion recomendada: Cambiar MONGO_INITDB_ROOT_PASSWORD en .env por una contrasena
  de al menos 20 caracteres alfanumericos con simbolos.

### Riesgo 4: Flask en modo debug en produccion
- Descripcion: FLASK_ENV=development activa el modo debug, que expone informacion
  interna del servidor ante errores. Riesgo en ambientes publicos.
- Mitigacion recomendada: Cambiar a FLASK_ENV=production y usar Gunicorn en vez de
  el servidor de desarrollo de Flask para produccion real.

### Riesgo 5: Sin autenticacion de usuarios
- Descripcion: Cualquier persona que acceda a la URL puede ver y modificar los datos.
  Para uso personal en red local esto es aceptable; en internet no.
- Mitigacion recomendada: Implementar autenticacion con JWT (JSON Web Tokens) y
  agregar un sistema de login antes de exponer en internet.

---

## Reflexion Final

### Por que es importante separar los servicios?
Separar en microservicios permite que cada parte del sistema sea independiente:
si el frontend falla, el backend y la base de datos siguen funcionando. Ademas,
cada servicio puede actualizarse, escalarse o reemplazarse sin afectar a los demas.
Por ejemplo, se podria cambiar Vue por React sin tocar el backend.

### Que riesgos existen si se expone la base de datos directamente?
Si MongoDB estuviera expuesto al exterior, un atacante podria conectarse sin
necesitar el usuario/contrasena si hay una mala configuracion, leer o borrar
todos los datos, y evitar por completo la logica de validacion del backend.
Es uno de los errores de configuracion mas comunes y peligrosos.

### Que ventajas ofrece Docker en esta arquitectura?
Docker garantiza que el proyecto funciona igual en cualquier maquina (elimina el
"en mi maquina funciona"). Facilita la instalacion con un solo comando, aisla
las dependencias de cada servicio, y permite escalar horizontalmente agregando
mas contenedores del mismo servicio segun demanda.

### Como se podria llevar esto a la nube?
Se podria desplegar en servicios como AWS ECS, Google Cloud Run o Azure Container
Instances. El docker-compose.yml se puede convertir a un archivo de Kubernetes
(usando Kompose). MongoDB se reemplazaria por MongoDB Atlas para mayor durabilidad.
El frontend se serviria desde un CDN como CloudFront o Cloudflare para mejor
rendimiento global.
