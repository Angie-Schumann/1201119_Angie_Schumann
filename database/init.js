// =============================================================
// SCRIPT DE INICIALIZACION DE MONGODB
// Este archivo se ejecuta automaticamente la primera vez
// que se levanta el contenedor de MongoDB.
// Crea la base de datos y las colecciones con validacion basica.
// =============================================================

// Selecciona (o crea) la base de datos del proyecto
db = db.getSiblingDB('medicamentos_db');

// -----------------------------------------------------------
// COLECCION: medicamentos
// Guarda los medicamentos que el usuario debe tomar
// -----------------------------------------------------------
db.createCollection('medicamentos', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['nombre', 'dosis', 'frecuencia'],  // Campos obligatorios
      properties: {
        nombre:      { bsonType: 'string', description: 'Nombre del medicamento' },
        dosis:       { bsonType: 'string', description: 'Dosis por toma (ej: 500mg)' },
        frecuencia:  { bsonType: 'string', description: 'Cada cuantas horas o veces al dia' },
        indicaciones:{ bsonType: 'string', description: 'Instrucciones adicionales' },
        activo:      { bsonType: 'bool',   description: 'Si el medicamento esta activo' }
      }
    }
  }
});

// -----------------------------------------------------------
// COLECCION: citas
// Guarda las citas medicas del usuario
// -----------------------------------------------------------
db.createCollection('citas', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['doctor', 'fecha', 'especialidad'],
      properties: {
        doctor:       { bsonType: 'string', description: 'Nombre del medico' },
        especialidad: { bsonType: 'string', description: 'Especialidad medica' },
        fecha:        { bsonType: 'string', description: 'Fecha de la cita ISO format' },
        hora:         { bsonType: 'string', description: 'Hora de la cita' },
        lugar:        { bsonType: 'string', description: 'Clinica o hospital' },
        notas:        { bsonType: 'string', description: 'Notas adicionales' },
        completada:   { bsonType: 'bool',   description: 'Si la cita ya paso' }
      }
    }
  }
});

// Inserta datos de ejemplo para probar el sistema desde el primer arranque
db.medicamentos.insertMany([
  {
    nombre: 'Losartan 50mg',
    dosis: '1 tableta',
    frecuencia: 'Una vez al dia en la manana',
    indicaciones: 'Tomar con agua, puede tomarse con o sin alimentos',
    activo: true,
    creadoEn: new Date()
  },
  {
    nombre: 'Metformina 850mg',
    dosis: '1 tableta',
    frecuencia: 'Dos veces al dia (manana y noche)',
    indicaciones: 'Tomar con las comidas para reducir malestar estomacal',
    activo: true,
    creadoEn: new Date()
  }
]);

db.citas.insertMany([
  {
    doctor: 'Dr. Carlos Mendez',
    especialidad: 'Cardiologia',
    fecha: '2026-06-15',
    hora: '10:00',
    lugar: 'Hospital General',
    notas: 'Llevar resultados de examen de sangre del mes pasado',
    completada: false,
    creadoEn: new Date()
  }
]);

print('Base de datos inicializada correctamente con datos de ejemplo.');
