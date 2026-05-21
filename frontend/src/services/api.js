// =============================================================
// SERVICES/API.JS - Capa de comunicacion con el Backend
// Centraliza todas las peticiones HTTP al backend Flask.
// Usar un archivo dedicado evita repetir la URL base en cada
// componente y facilita cambiarla en un solo lugar.
// =============================================================

import axios from 'axios'

// Lee la URL del backend desde la variable de entorno de Vite
// VITE_API_URL viene del archivo .env y se inyecta en tiempo de build
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5510/api'

// Crea una instancia de axios pre-configurada
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,                              // Espera max 10 segundos por respuesta
  headers: { 'Content-Type': 'application/json' }  // Siempre envia JSON
})

// Interceptor de respuesta: manejo global de errores
// Se ejecuta automaticamente despues de CADA peticion
api.interceptors.response.use(
  // Si la peticion fue exitosa, devuelve la respuesta sin cambios
  response => response,
  
  // Si hubo un error, lo captura y muestra un mensaje util
  error => {
    if (error.code === 'ERR_NETWORK') {
      console.error('[API] Error de red: el backend no esta disponible')
    } else if (error.response) {
      console.error(`[API] Error ${error.response.status}:`, error.response.data)
    }
    return Promise.reject(error)  // Propaga el error para manejarlo en el componente
  }
)

// =============================================================
// METODOS PARA MEDICAMENTOS
// =============================================================
export const medicamentosAPI = {
  // Obtiene todos los medicamentos
  obtenerTodos: () => api.get('/medicamentos'),
  
  // Crea un medicamento nuevo (envia el objeto como JSON en el body)
  crear: (datos) => api.post('/medicamentos', datos),
  
  // Actualiza un medicamento por ID
  actualizar: (id, datos) => api.put(`/medicamentos/${id}`, datos),
  
  // Elimina un medicamento por ID
  eliminar: (id) => api.delete(`/medicamentos/${id}`)
}

// =============================================================
// METODOS PARA CITAS MEDICAS
// =============================================================
export const citasAPI = {
  // Obtiene todas las citas, con filtro opcional por estado
  // Ejemplo: obtenerTodas({ completada: false }) -> solo pendientes
  obtenerTodas: (filtros = {}) => api.get('/citas', { params: filtros }),
  
  // Crea una cita nueva
  crear: (datos) => api.post('/citas', datos),
  
  // Actualiza una cita (tambien se usa para marcarla completada)
  actualizar: (id, datos) => api.put(`/citas/${id}`, datos),
  
  // Elimina una cita
  eliminar: (id) => api.delete(`/citas/${id}`)
}

// Exporta el cliente base para verificar salud del backend
export const healthCheck = () => api.get('/health')

export default api
