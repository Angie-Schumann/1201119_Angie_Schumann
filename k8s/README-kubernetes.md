# Vitalis - Despliegue en Kubernetes

Guia completa para desplegar la aplicacion Vitalis en Kubernetes local con Docker Desktop.

---

## Estructura de archivos k8s/

```
k8s/
├── mongo-secret.yml        <- Credenciales seguras (equivalente al .env)
├── mongo-deployment.yml    <- Base de datos MongoDB + su Service de red
├── backend-deployment.yml  <- API Flask + su Service de red
└── frontend-deployment.yml <- Interfaz Vue/Nginx + su Service de red
```

---

## Conceptos clave antes de empezar

- **Pod**: La unidad minima de Kubernetes. Contiene uno o mas contenedores.
- **Deployment**: Controlador que garantiza que los Pods esten siempre corriendo.
- **Service**: Da una direccion de red fija a los Pods (como el nombre de servicio en Docker).
- **Secret**: Guarda datos sensibles como contrasenas (equivalente al .env).
- **NodePort**: Tipo de Service que abre un puerto en el nodo para acceso externo.
- **PVC**: Solicitud de espacio en disco persistente para la base de datos.

---

## Puertos del sistema en Kubernetes

| Servicio  | Puerto interno | Puerto externo (nodePort) | Acceso            |
|-----------|---------------|--------------------------|-------------------|
| Frontend  | 80            | 30080                    | http://localhost:30080 |
| Backend   | 5000          | 30510                    | http://localhost:30510 |
| MongoDB   | 27017         | Ninguno (ClusterIP)      | Solo interno       |

---

## Pasos para desplegar

### Paso 1: Construir las imagenes Docker localmente

Kubernetes con imagePullPolicy:Never busca imagenes locales.
Primero hay que construirlas con Docker:

```bash
# Posicionarse en la carpeta raiz del proyecto
cd C:\Users\apsch\Desktop\1201119_Angie_Schumann

# Construir la imagen del backend
docker build -t vitalis-backend:latest ./backend

# Construir la imagen del frontend
docker build -t vitalis-frontend:latest ./frontend
```

Verificar que las imagenes existen:
```bash
docker images | findstr vitalis
```

### Paso 2: Cargar las imagenes en el cluster kind

Kind usa su propio almacenamiento interno. Hay que cargar las imagenes:

```bash
kind load docker-image vitalis-backend:latest --name desktop
kind load docker-image vitalis-frontend:latest --name desktop
```

### Paso 3: Aplicar los archivos en orden

El orden importa: primero el Secret, luego MongoDB, luego Backend, luego Frontend.

```bash
# Ir a la carpeta k8s
cd C:\Users\apsch\Desktop\1201119_Angie_Schumann\k8s

# 1. Crear el Secret con las credenciales
kubectl apply -f mongo-secret.yml

# 2. Desplegar MongoDB y su Service
kubectl apply -f mongo-deployment.yml

# 3. Desplegar el Backend y su Service
kubectl apply -f backend-deployment.yml

# 4. Desplegar el Frontend y su Service
kubectl apply -f frontend-deployment.yml
```

### Paso 4: Verificar que todo este corriendo

```bash
# Ver los Pods (deben estar en estado Running)
kubectl get pods

# Ver los Deployments
kubectl get deployments

# Ver los Services y sus puertos
kubectl get services
```

Resultado esperado en kubectl get pods:
```
NAME                                    READY   STATUS    RESTARTS
mongo-deployment-xxxx                   1/1     Running   0
backend-deployment-xxxx                 1/1     Running   0
frontend-deployment-xxxx                1/1     Running   0
```

### Paso 5: Acceder a la aplicacion

Abrir el navegador en:
```
http://localhost:30080
```

Verificar el backend:
```
http://localhost:30510/api/health
```

---

## Comandos utiles para el laboratorio

```bash
# Ver logs de un Pod (reemplazar xxxx con el nombre real del pod)
kubectl logs mongo-deployment-xxxx
kubectl logs backend-deployment-xxxx
kubectl logs frontend-deployment-xxxx

# Ver detalles de un Pod (util para depurar errores)
kubectl describe pod nombre-del-pod

# Ver los nodos del cluster
kubectl get nodes

# Eliminar todo lo desplegado
kubectl delete -f mongo-secret.yml
kubectl delete -f mongo-deployment.yml
kubectl delete -f backend-deployment.yml
kubectl delete -f frontend-deployment.yml
```

---

## Diferencias entre Docker Compose y Kubernetes

| Concepto Docker Compose | Equivalente Kubernetes |
|------------------------|----------------------|
| docker-compose.yml     | Multiples archivos .yml |
| service: mongo         | Deployment + Service   |
| .env                   | Secret                 |
| volumes:               | PersistentVolumeClaim  |
| networks:              | Services (ClusterIP)   |
| ports: 80:80           | NodePort               |
| depends_on:            | No existe, se maneja con readiness probes |
