#!/bin/bash
# =============================================================
# INICIAR.SH - Script para levantar Vitalis en Kubernetes
#
# Este script hace tres cosas:
# 1. Reinicia el backend para garantizar conexion con MongoDB
# 2. Abre un tunel al frontend (Vue) en el puerto 8080
# 3. Abre un tunel al backend (Flask) en el puerto 5510
#
# Por que reiniciar el backend?
# Kubernetes arranca todos los pods casi al mismo tiempo.
# A veces Flask arranca antes que MongoDB este listo,
# entonces la conexion falla y db queda como None para siempre.
# Reiniciando el backend cuando MongoDB ya esta estable,
# la conexion se establece correctamente.
#
# COMO USARLO:
# Abre Git Bash, ve a la carpeta k8s y corre:
#   bash iniciar.sh
#
# COMO DETENERLO:
# Presiona Ctrl+C en esta misma terminal
# =============================================================

echo "============================================"
echo "  Iniciando Vitalis en Kubernetes..."
echo "============================================"

# Muestra el estado actual de los Pods antes de hacer nada
echo ""
echo "Estado de los Pods:"
kubectl get pods
echo ""

# Reinicia el backend para asegurar que se conecte bien a MongoDB
# Esto es necesario porque Flask puede haber arrancado antes que MongoDB
echo "Reiniciando backend para asegurar conexion con MongoDB..."
kubectl rollout restart deployment/backend-deployment

# Espera 20 segundos para que el nuevo Pod del backend arranque completamente
# y establezca la conexion con MongoDB antes de abrir los tuneles
echo "Esperando que el backend arranque..."
sleep 20

# Levanta el tunel del frontend en segundo plano
# El & al final significa "ejecuta esto en segundo plano y sigue"
kubectl port-forward service/frontend-service 8080:80 &

# Guarda el ID del proceso del frontend para poder cerrarlo despues
PID_FRONTEND=$!

# Espera un segundo para que el primer tunel arranque
sleep 1

# Levanta el tunel del backend en segundo plano
kubectl port-forward service/backend-service 5510:5000 &

# Guarda el ID del proceso del backend
PID_BACKEND=$!

echo "============================================"
echo "  Vitalis esta corriendo!"
echo ""
echo "  Frontend: http://localhost:8080"
echo "  Backend:  http://localhost:5510/api/health"
echo ""
echo "  Presiona Ctrl+C para detener todo"
echo "============================================"

# Funcion que se ejecuta cuando presionas Ctrl+C
# Cierra los dos procesos en segundo plano limpiamente
cleanup() {
    echo ""
    echo "Deteniendo Vitalis..."
    kill $PID_FRONTEND 2>/dev/null   # Cierra el tunel del frontend
    kill $PID_BACKEND 2>/dev/null    # Cierra el tunel del backend
    echo "Listo. Hasta luego!"
    exit 0
}

# Le dice al script que cuando detecte Ctrl+C, ejecute la funcion cleanup
trap cleanup SIGINT SIGTERM

# Mantiene el script corriendo hasta que presiones Ctrl+C
wait