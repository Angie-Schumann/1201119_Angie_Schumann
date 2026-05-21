<template>
  <!-- 
    DASHBOARD.VUE - Vista de inicio
    Muestra un resumen rapido del estado de salud del usuario:
    cuantos medicamentos activos tiene y cuantas citas pendientes.
  -->
  <div>

    <!-- Cabecera de la pagina -->
    <div class="page-header">
      <h2>Bienvenido a Vitalis</h2>
      
    </div>

    <!-- Alerta si el backend no esta disponible -->
    <div v-if="errorConexion" class="alerta alerta-error">
      <span>⚠️</span>
      No se pudo conectar con el servidor. Verifica que el backend este corriendo.
    </div>

    <!-- Spinner de carga mientras se obtienen los datos -->
    <div v-if="cargando" class="spinner"></div>

    <!-- Contenido principal cuando ya cargaron los datos -->
    <div v-else>

      <!-- Tarjetas de resumen estadistico -->
      <div class="cards-grid" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); margin-bottom: 28px;">

        <!-- Card: Medicamentos activos -->
        <div class="card stat-card">
          <div class="stat-icono" style="background: #EFF6FF;">💊</div>
          <div>
            <div class="stat-numero">{{ totalMedicamentos }}</div>
            <div class="stat-label">Medicamentos activos</div>
          </div>
        </div>

        <!-- Card: Citas pendientes -->
        <div class="card stat-card">
          <div class="stat-icono" style="background: #F0FFFE;">📅</div>
          <div>
            <div class="stat-numero">{{ citasPendientes }}</div>
            <div class="stat-label">Citas pendientes</div>
          </div>
        </div>

        <!-- Card: Proxima cita -->
        <div class="card stat-card">
          <div class="stat-icono" style="background: #FFF7ED;">🩺</div>
          <div>
            <div class="stat-numero" style="font-size: 1rem;">
              {{ proximaCita ? formatearFechaCorta(proximaCita.fecha) : 'Ninguna' }}
            </div>
            <div class="stat-label">Proxima cita</div>
          </div>
        </div>

      </div>

      <!-- Seccion: proximas citas -->
      <div class="card" style="margin-bottom: 20px;">
        <div class="flex items-center justify-between mb-4">
          <h3 style="font-family: 'Lora', serif; font-size: 1.1rem;">
            Proximas Citas
          </h3>
          <router-link to="/citas" class="btn btn-secundario btn-sm">
            Ver todas
          </router-link>
        </div>

        <!-- Lista de las 3 proximas citas -->
        <div v-if="citasRecientes.length === 0" class="text-suave text-center" style="padding: 20px 0;">
          No tienes citas programadas
        </div>

        <div v-else class="lista-citas-preview">
          <div 
            v-for="cita in citasRecientes" 
            :key="cita._id"
            class="item-preview"
          >
            <div class="item-preview-icono">🩺</div>
            <div class="item-preview-info">
              <strong>{{ cita.doctor }}</strong>
              <span class="text-suave">{{ cita.especialidad }} &bull; {{ formatearFecha(cita.fecha) }}</span>
            </div>
            <span class="badge badge-pendiente">{{ cita.hora || 'Sin hora' }}</span>
          </div>
        </div>
      </div>

      <!-- Seccion: medicamentos activos -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 style="font-family: 'Lora', serif; font-size: 1.1rem;">
            Mis Medicamentos
          </h3>
          <router-link to="/medicamentos" class="btn btn-secundario btn-sm">
            Gestionar
          </router-link>
        </div>

        <div v-if="medicamentosActivos.length === 0" class="text-suave text-center" style="padding: 20px 0;">
          No tienes medicamentos registrados
        </div>

        <div v-else class="lista-citas-preview">
          <div 
            v-for="med in medicamentosActivos" 
            :key="med._id"
            class="item-preview"
          >
            <div class="item-preview-icono">💊</div>
            <div class="item-preview-info">
              <strong>{{ med.nombre }}</strong>
              <span class="text-suave">{{ med.dosis }} &bull; {{ med.frecuencia }}</span>
            </div>
            <span class="badge badge-activo">Activo</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
// Importa las funciones reactivas de Vue 3 (Composition API)
import { ref, computed, onMounted } from 'vue'

// Importa los servicios de API centralizados
import { medicamentosAPI, citasAPI, healthCheck } from '../services/api.js'

// =============================================================
// ESTADO REACTIVO
// ref() crea variables reactivas: cuando cambian, Vue actualiza el HTML
// =============================================================
const medicamentos = ref([])   // Lista de medicamentos desde el backend
const citas        = ref([])   // Lista de citas desde el backend
const cargando     = ref(true) // Muestra spinner mientras carga
const errorConexion = ref(false)

// =============================================================
// COMPUTED: valores derivados del estado
// Se recalculan automaticamente cuando cambia el estado base
// =============================================================
const totalMedicamentos = computed(() =>
  // Cuenta solo los medicamentos con activo === true
  medicamentos.value.filter(m => m.activo).length
)

const citasPendientes = computed(() =>
  // Cuenta las citas que aun no estan completadas
  citas.value.filter(c => !c.completada).length
)

const citasRecientes = computed(() =>
  // Toma las 3 primeras citas pendientes (ya vienen ordenadas por fecha)
  citas.value.filter(c => !c.completada).slice(0, 3)
)

const proximaCita = computed(() =>
  // La primera cita pendiente es la mas proxima
  citas.value.find(c => !c.completada)
)

const medicamentosActivos = computed(() =>
  medicamentos.value.filter(m => m.activo).slice(0, 4)
)

// =============================================================
// FUNCIONES DE FORMATO DE FECHAS
// =============================================================
function formatearFecha(fechaStr) {
  if (!fechaStr) return 'Sin fecha'
  const fecha = new Date(fechaStr + 'T00:00:00')  // Evita problemas de zona horaria
  return fecha.toLocaleDateString('es-GT', {
    weekday: 'long', day: 'numeric', month: 'long'
  })
}

function formatearFechaCorta(fechaStr) {
  if (!fechaStr) return '-'
  const fecha = new Date(fechaStr + 'T00:00:00')
  return fecha.toLocaleDateString('es-GT', { day: 'numeric', month: 'short' })
}

// =============================================================
// CARGA DE DATOS AL MONTAR EL COMPONENTE
// onMounted se ejecuta cuando el componente aparece en pantalla
// =============================================================
onMounted(async () => {
  try {
    // Primero verifica que el backend este disponible
    await healthCheck()
    
    // Carga medicamentos y citas en paralelo (mas rapido que secuencial)
    const [resMeds, resCitas] = await Promise.all([
      medicamentosAPI.obtenerTodos(),
      citasAPI.obtenerTodas({ completada: false })  // Solo pendientes para el dashboard
    ])
    
    medicamentos.value = resMeds.data.datos
    citas.value = resCitas.data.datos
    
  } catch (error) {
    // Si falla la conexion, muestra la alerta de error
    errorConexion.value = true
    console.error('[Dashboard] Error al cargar datos:', error)
  } finally {
    // finally se ejecuta siempre, con o sin error
    cargando.value = false
  }
})
</script>

<style scoped>
/* Estilos especificos del Dashboard (no afectan otros componentes) */

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icono {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-numero {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-texto);
  line-height: 1;
}

.stat-label {
  font-size: 0.82rem;
  color: var(--color-texto-suave);
  margin-top: 4px;
}

/* Lista de items preview en el dashboard */
.lista-citas-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-preview {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px;
  background: var(--color-fondo);
  border-radius: 10px;
  border: 1px solid var(--color-borde);
}

.item-preview-icono {
  font-size: 1.3rem;
  min-width: 32px;
  text-align: center;
}

.item-preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-preview-info strong {
  font-size: 0.92rem;
  color: var(--color-texto);
}

.item-preview-info span {
  font-size: 0.8rem;
}
</style>
