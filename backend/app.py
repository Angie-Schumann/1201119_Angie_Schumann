# =============================================================
# APP.PY - BACKEND FLASK
# API REST para gestionar medicamentos y citas medicas
# Se conecta a MongoDB usando pymongo
# =============================================================

import os                           # Para leer variables de entorno del sistema
from flask import Flask, request, jsonify   # Flask core: app, request data, JSON responses
from flask_cors import CORS                 # Para permitir peticiones desde el frontend Vue
from pymongo import MongoClient             # Cliente de MongoDB para Python
from pymongo.errors import ConnectionFailure, PyMongoError  # Manejo de errores de BD
from bson import ObjectId                   # MongoDB usa ObjectId en vez de int para IDs
from bson.errors import InvalidId           # Error al convertir un ID invalido
from dotenv import load_dotenv              # Carga el archivo .env
from datetime import datetime               # Para manejar fechas

# Carga las variables definidas en el archivo .env al entorno
load_dotenv()

# =============================================================
# INICIALIZACION DE FLASK
# =============================================================
app = Flask(__name__)

# Carga la clave secreta desde .env (necesaria para seguridad en Flask)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback_key_cambiar')

# =============================================================
# CONFIGURACION DE CORS
# Permite que el frontend (corriendo en otro puerto/origen)
# pueda hacer peticiones HTTP al backend sin ser bloqueado
# por la politica de seguridad del navegador (Same-Origin Policy)
# =============================================================
# Para uso local se permite cualquier origen.
# El navegador puede enviar http://localhost sin puerto
# dependiendo del SO, por eso se acepta cualquier origen local.
CORS(app)

# =============================================================
# CONEXION A MONGODB
# Usa el URI del archivo .env. El hostname "mongo" es el nombre
# del servicio definido en docker-compose.yml, NO localhost.
# Docker resuelve ese nombre automaticamente dentro de la red.
# =============================================================
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:password@mongo:27017/medicamentos_db?authSource=admin')

try:
    # Crea el cliente de conexion a MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Fuerza la verificacion de conexion al arrancar
    client.admin.command('ping')
    
    # Selecciona la base de datos
    db = client['medicamentos_db']
    
    print("[OK] Conexion a MongoDB exitosa")
    
except ConnectionFailure as e:
    # Si no puede conectar, imprime el error (el contenedor seguira corriendo)
    print(f"[ERROR] No se pudo conectar a MongoDB: {e}")
    db = None


# =============================================================
# FUNCION AUXILIAR: Convierte ObjectId de MongoDB a string
# MongoDB devuelve documentos con "_id" de tipo ObjectId.
# JSON no puede serializar ObjectId directamente, entonces
# lo convertimos a string antes de enviar la respuesta.
# =============================================================
def serializar_documento(doc):
    """Convierte un documento de MongoDB a dict serializable en JSON."""
    if doc:
        doc['_id'] = str(doc['_id'])   # ObjectId -> "64abc123def..."
    return doc

def serializar_lista(lista):
    """Serializa una lista de documentos de MongoDB."""
    return [serializar_documento(doc) for doc in lista]


# =============================================================
# RUTA DE SALUD (Health Check)
# Permite verificar que el backend esta corriendo correctamente
# Util para Docker y para depurar
# =============================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica que el backend y la conexion a MongoDB esten activos."""
    estado_mongo = "conectado" if db is not None else "desconectado"
    return jsonify({
        "status": "ok",
        "servicio": "Vitalis Backend",
        "mongodb": estado_mongo,
        "timestamp": datetime.now().isoformat()
    }), 200


# =============================================================
# RUTAS DE MEDICAMENTOS
# CRUD completo: Crear, Leer, Actualizar, Eliminar
# =============================================================

@app.route('/api/medicamentos', methods=['GET'])
def obtener_medicamentos():
    """
    GET /api/medicamentos
    Devuelve todos los medicamentos registrados.
    El frontend llama esta ruta al cargar la seccion de medicamentos.
    """
    try:
        # Busca todos los documentos en la coleccion "medicamentos"
        # sort ordena por fecha de creacion descendente (mas reciente primero)
        medicamentos = list(db['medicamentos'].find().sort('creadoEn', -1))
        
        return jsonify({
            "ok": True,
            "datos": serializar_lista(medicamentos),  # Lista de medicamentos como JSON
            "total": len(medicamentos)                # Cuantos hay en total
        }), 200
        
    except PyMongoError as e:
        # Error de base de datos
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/medicamentos', methods=['POST'])
def crear_medicamento():
    """
    POST /api/medicamentos
    Crea un nuevo medicamento. Recibe los datos en formato JSON
    en el cuerpo de la peticion desde el frontend.
    """
    try:
        # Obtiene el JSON que envio el frontend
        datos = request.get_json()
        
        # Validacion: verifica que los campos obligatorios existan y no esten vacios
        campos_requeridos = ['nombre', 'dosis', 'frecuencia']
        for campo in campos_requeridos:
            if not datos.get(campo):   # .get() evita KeyError si el campo no existe
                return jsonify({
                    "ok": False,
                    "error": f"El campo '{campo}' es obligatorio"
                }), 400   # 400 = Bad Request
        
        # Construye el documento que se insertara en MongoDB
        nuevo_medicamento = {
            "nombre":       datos['nombre'].strip(),           # .strip() elimina espacios extras
            "dosis":        datos['dosis'].strip(),
            "frecuencia":   datos['frecuencia'].strip(),
            "indicaciones": datos.get('indicaciones', '').strip(),  # Opcional
            "activo":       True,                              # Activo por defecto
            "creadoEn":     datetime.now()                    # Fecha de creacion
        }
        
        # Inserta en MongoDB y obtiene el ID generado automaticamente
        resultado = db['medicamentos'].insert_one(nuevo_medicamento)
        
        # Agrega el ID al documento para devolverlo en la respuesta
        nuevo_medicamento['_id'] = str(resultado.inserted_id)
        
        return jsonify({
            "ok": True,
            "mensaje": "Medicamento creado correctamente",
            "datos": serializar_documento(nuevo_medicamento)
        }), 201   # 201 = Created
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/medicamentos/<id>', methods=['PUT'])
def actualizar_medicamento(id):
    """
    PUT /api/medicamentos/<id>
    Actualiza un medicamento existente por su ID.
    El <id> viene en la URL, los datos nuevos en el cuerpo JSON.
    """
    try:
        # Convierte el string del ID al tipo ObjectId de MongoDB
        oid = ObjectId(id)
    except InvalidId:
        # Si el ID no tiene el formato correcto de MongoDB
        return jsonify({"ok": False, "error": "ID invalido"}), 400
    
    try:
        datos = request.get_json()
        
        # Construye el objeto de actualizacion
        # Solo actualiza los campos que vengan en la peticion
        campos_a_actualizar = {}
        for campo in ['nombre', 'dosis', 'frecuencia', 'indicaciones', 'activo']:
            if campo in datos:
                campos_a_actualizar[campo] = datos[campo]
        
        campos_a_actualizar['actualizadoEn'] = datetime.now()
        
        # $set actualiza solo los campos especificados, no borra el resto
        resultado = db['medicamentos'].update_one(
            {"_id": oid},                    # Filtro: busca por ID
            {"$set": campos_a_actualizar}    # Actualizacion parcial
        )
        
        if resultado.matched_count == 0:
            return jsonify({"ok": False, "error": "Medicamento no encontrado"}), 404
        
        return jsonify({"ok": True, "mensaje": "Medicamento actualizado"}), 200
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/medicamentos/<id>', methods=['DELETE'])
def eliminar_medicamento(id):
    """
    DELETE /api/medicamentos/<id>
    Elimina un medicamento por su ID.
    """
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"ok": False, "error": "ID invalido"}), 400
    
    try:
        resultado = db['medicamentos'].delete_one({"_id": oid})
        
        if resultado.deleted_count == 0:
            return jsonify({"ok": False, "error": "Medicamento no encontrado"}), 404
        
        return jsonify({"ok": True, "mensaje": "Medicamento eliminado"}), 200
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# =============================================================
# RUTAS DE CITAS MEDICAS
# CRUD completo para gestionar citas con doctores
# =============================================================

@app.route('/api/citas', methods=['GET'])
def obtener_citas():
    """
    GET /api/citas
    Devuelve todas las citas medicas.
    Admite filtro por ?completada=true/false en la URL.
    """
    try:
        filtro = {}
        
        # Si viene el parametro "completada" en la URL, filtra por ese estado
        # Ejemplo: GET /api/citas?completada=false -> solo citas pendientes
        completada_param = request.args.get('completada')
        if completada_param is not None:
            filtro['completada'] = completada_param.lower() == 'true'
        
        # Ordena por fecha ascendente (la proxima cita primero)
        citas = list(db['citas'].find(filtro).sort('fecha', 1))
        
        return jsonify({
            "ok": True,
            "datos": serializar_lista(citas),
            "total": len(citas)
        }), 200
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/citas', methods=['POST'])
def crear_cita():
    """
    POST /api/citas
    Crea una nueva cita medica.
    """
    try:
        datos = request.get_json()
        
        # Valida campos obligatorios
        campos_requeridos = ['doctor', 'fecha', 'especialidad']
        for campo in campos_requeridos:
            if not datos.get(campo):
                return jsonify({
                    "ok": False,
                    "error": f"El campo '{campo}' es obligatorio"
                }), 400
        
        nueva_cita = {
            "doctor":       datos['doctor'].strip(),
            "especialidad": datos['especialidad'].strip(),
            "fecha":        datos['fecha'],
            "hora":         datos.get('hora', '').strip(),
            "lugar":        datos.get('lugar', '').strip(),
            "notas":        datos.get('notas', '').strip(),
            "completada":   False,         # Nueva cita siempre pendiente
            "creadoEn":     datetime.now()
        }
        
        resultado = db['citas'].insert_one(nueva_cita)
        nueva_cita['_id'] = str(resultado.inserted_id)
        
        return jsonify({
            "ok": True,
            "mensaje": "Cita creada correctamente",
            "datos": serializar_documento(nueva_cita)
        }), 201
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/citas/<id>', methods=['PUT'])
def actualizar_cita(id):
    """
    PUT /api/citas/<id>
    Actualiza una cita existente.
    Tambien se usa para marcarla como completada.
    """
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"ok": False, "error": "ID invalido"}), 400
    
    try:
        datos = request.get_json()
        
        campos_a_actualizar = {}
        for campo in ['doctor', 'especialidad', 'fecha', 'hora', 'lugar', 'notas', 'completada']:
            if campo in datos:
                campos_a_actualizar[campo] = datos[campo]
        
        campos_a_actualizar['actualizadoEn'] = datetime.now()
        
        resultado = db['citas'].update_one(
            {"_id": oid},
            {"$set": campos_a_actualizar}
        )
        
        if resultado.matched_count == 0:
            return jsonify({"ok": False, "error": "Cita no encontrada"}), 404
        
        return jsonify({"ok": True, "mensaje": "Cita actualizada"}), 200
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/citas/<id>', methods=['DELETE'])
def eliminar_cita(id):
    """
    DELETE /api/citas/<id>
    Elimina una cita medica por su ID.
    """
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"ok": False, "error": "ID invalido"}), 400
    
    try:
        resultado = db['citas'].delete_one({"_id": oid})
        
        if resultado.deleted_count == 0:
            return jsonify({"ok": False, "error": "Cita no encontrada"}), 404
        
        return jsonify({"ok": True, "mensaje": "Cita eliminada"}), 200
        
    except PyMongoError as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# =============================================================
# PUNTO DE ENTRADA
# Se ejecuta cuando corres "python app.py"
# host='0.0.0.0' hace que Flask escuche en todas las interfaces,
# necesario para que Docker pueda redirigir el trafico al contenedor
# =============================================================
if __name__ == '__main__':
    puerto = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"[INFO] Iniciando MediTrack Backend en puerto {puerto}")
    print(f"[INFO] Modo: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',    # Escucha en todas las interfaces de red del contenedor
        port=puerto,        # Puerto definido en .env
        debug=(os.getenv('FLASK_ENV') == 'development')  # Debug solo en desarrollo
    )
