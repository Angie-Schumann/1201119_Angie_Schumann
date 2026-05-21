<template>
  <!--
    CITAS.VUE - Vista de gestion de citas medicas
    Permite registrar, ver, editar, completar y eliminar citas.
    Incluye filtro para ver solo pendientes o todas.
  -->
  <div>

    <!-- Cabecera con titulo y boton agregar -->
    <div class="page-header flex items-center justify-between">
      <div>
        <h2>Citas Medicas</h2>
        <p>Organiza y da seguimiento a tus consultas</p>
      </div>
      <button class="btn btn-primario" @click="abrirModalNuevo">
        <span>+</span> Agendar Cita
      </button>
    </div>

    <!-- Filtros de estado -->
    <div class="filtros-wrap">
      <button 
        :class="['filtro-btn', filtroActivo === 'pendientes' ? 'activo' : '']"
        @click="cambiarFiltro('pendientes')"
      >
        Pendientes
        <!-- Badge con el conteo -->
        <span class="filtro-count">{{ contarPendientes }}</span>
      </button>
      <button 
        :class="['filtro-btn', filtroActivo === 'todas' ? 'activo' : '']"
        @click="cambiarFiltro('todas')"
      >
        Todas
      </button>
      <button 
        :class="['filtro-btn', filtroActivo === 'completadas' ? 'activo' : '']"
        @click="cambiarFiltro('completadas')"
      >
        Completadas
      </button>
    </div>

    <!-- Toast de exito (esquina superior derecha) -->
    <transition name="toast">
      <div v-if="exito" class="toast toast-exito">✓ {{ exito }}</div>
    </transition>
    <transition name="toast">
      <div v-if="error" class="toast toast-error">⚠ {{ error }}</div>
    </transition>

    <!-- Spinner de carga -->
    <div v-if="cargando" class="spinner"></div>

    <!-- Estado vacio -->
    <div v-else-if="citasFiltradas.length === 0" class="card estado-vacio">
      <div class="icono-grande">📅</div>
      <h3>Sin citas en esta seccion</h3>
      <p>
        {{ filtroActivo === 'pendientes' 
            ? 'No tienes citas pendientes. Agenda una nueva arriba.' 
            : 'No hay citas que mostrar con este filtro.' 
        }}
      </p>
    </div>

    <!-- Lista de citas -->
    <div v-else class="lista-citas">
      <div 
        v-for="cita in citasFiltradas"
        :key="cita._id"
        :class="['card', 'cita-card', cita.completada ? 'cita-completada' : '']"
      >
        <!-- Encabezado de la cita -->
        <div class="flex items-center justify-between" style="margin-bottom: 14px;">
          <div class="flex items-center gap-2">
            <span class="cita-icono">🩺</span>
            <div>
              <h3 class="cita-doctor">{{ cita.doctor }}</h3>
              <span class="cita-especialidad">{{ cita.especialidad }}</span>
            </div>
          </div>
          <span :class="['badge', cita.completada ? 'badge-completada' : 'badge-pendiente']">
            {{ cita.completada ? 'Completada' : 'Pendiente' }}
          </span>
        </div>

        <!-- Detalles en grilla de 2 columnas -->
        <div class="cita-detalles-grid">
          <div class="cita-detalle">
            <span class="cita-detalle-label">Fecha</span>
            <span class="cita-detalle-valor">{{ formatearFecha(cita.fecha) }}</span>
          </div>
          <div class="cita-detalle">
            <span class="cita-detalle-label">Hora</span>
            <span class="cita-detalle-valor">{{ cita.hora || 'Por confirmar' }}</span>
          </div>
          <div v-if="cita.lugar" class="cita-detalle" style="grid-column: 1 / -1;">
            <span class="cita-detalle-label">Lugar</span>
            <span class="cita-detalle-valor">{{ cita.lugar }}</span>
          </div>
          <div v-if="cita.notas" class="cita-detalle" style="grid-column: 1 / -1;">
            <span class="cita-detalle-label">Notas</span>
            <span class="cita-detalle-valor" style="font-style: italic;">{{ cita.notas }}</span>
          </div>
        </div>

        <!-- Botones de accion -->
        <div class="flex gap-2" style="margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--color-borde);">
          
          <!-- Boton marcar como completada / pendiente -->
          <!-- Verde = marcar completada (accion positiva). Azul = marcar pendiente (accion neutral) -->
          <button 
            :class="['btn', 'btn-sm', cita.completada ? 'btn-pendiente' : 'btn-exito']"
            @click="toggleCompletada(cita)"
          >
            {{ cita.completada ? '↩ Pendiente' : '✓ Completada' }}
          </button>
          
          <button class="btn btn-secundario btn-sm" @click="abrirModalEditar(cita)">
            Editar
          </button>
          <button class="btn btn-peligro btn-sm" @click="confirmarEliminar(cita)">
            Eliminar
          </button>
        </div>

      </div>
    </div>


    <!-- =======================================================
         MODAL: Formulario nueva cita o edicion
         ======================================================= -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">

        <div class="modal-header">
          <h3>{{ editando ? 'Editar Cita' : 'Nueva Cita Medica' }}</h3>
          <button class="btn-cerrar" @click="cerrarModal">×</button>
        </div>

        <form @submit.prevent="guardarCita">

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px;">

            <div class="form-grupo" style="grid-column: 1 / -1;">
              <label>Nombre del doctor *</label>
              <input 
                v-model="formulario.doctor"
                type="text"
                placeholder="Dr. / Dra. Nombre Apellido"
                required
              />
            </div>

            <div class="form-grupo">
              <label>Especialidad *</label>
              <input 
                v-model="formulario.especialidad"
                type="text"
                placeholder="Ej: Cardiologia, Medicina general"
                required
              />
            </div>

            <div class="form-grupo">
              <label>Fecha *</label>
              <!-- type="date" muestra un selector de fecha del navegador -->
              <input 
                v-model="formulario.fecha"
                type="date"
                required
              />
            </div>

            <div class="form-grupo">
              <label>Hora</label>
              <input 
                v-model="formulario.hora"
                type="time"
                placeholder="10:30"
              />
            </div>

            <div class="form-grupo">
              <label>Clinica / Hospital</label>
              <input 
                v-model="formulario.lugar"
                type="text"
                placeholder="Nombre del lugar"
              />
            </div>

          </div>

          <div class="form-grupo">
            <label>Notas adicionales</label>
            <textarea 
              v-model="formulario.notas"
              placeholder="Recordatorios, documentos a llevar, instrucciones previas..."
            ></textarea>
          </div>

          <div v-if="errorModal" class="alerta alerta-error">{{ errorModal }}</div>

          <div class="form-acciones">
            <button type="button" class="btn btn-secundario" @click="cerrarModal">
              Cancelar
            </button>
            <button type="submit" class="btn btn-primario" :disabled="guardando">
              {{ guardando ? 'Guardando...' : (editando ? 'Actualizar' : 'Agendar Cita') }}
            </button>
          </div>

        </form>
      </div>
    </div>


    <!-- Modal de confirmacion para eliminar -->
    <div v-if="mostrarConfirmacion" class="modal-overlay" @click.self="mostrarConfirmacion = false">
      <div class="modal" style="max-width: 400px;">
        <div class="modal-header">
          <h3>Eliminar cita</h3>
          <button class="btn-cerrar" @click="mostrarConfirmacion = false">×</button>
        </div>
        <p style="color: var(--color-texto-suave); margin-bottom: 20px;">
          Se eliminara la cita con <strong>{{ citaAEliminar?.doctor }}</strong> 
          del <strong>{{ formatearFecha(citaAEliminar?.fecha) }}</strong>. 
          Esta accion no se puede deshacer.
        </p>
        <div class="form-acciones">
          <button class="btn btn-secundario" @click="mostrarConfirmacion = false">Cancelar</button>
          <button class="btn btn-peligro" @click="eliminarCita" :disabled="guardando">
            {{ guardando ? 'Eliminando...' : 'Eliminar cita' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { citasAPI } from '../services/api.js'

// =============================================================
// ESTADO REACTIVO
// =============================================================
const citas               = ref([])
const cargando            = ref(true)
const guardando           = ref(false)
const mostrarModal        = ref(false)
const mostrarConfirmacion = ref(false)
const editando            = ref(false)
const filtroActivo        = ref('pendientes')  // Filtro por defecto: pendientes
const error               = ref('')
const exito               = ref('')
const errorModal          = ref('')
const citaAEliminar       = ref(null)
const citaIdEditando      = ref(null)

const formulario = ref({
  doctor: '', especialidad: '', fecha: '', hora: '', lugar: '', notas: ''
})

// =============================================================
// COMPUTED: filtro de citas segun seleccion
// =============================================================
const citasFiltradas = computed(() => {
  if (filtroActivo.value === 'pendientes')  return citas.value.filter(c => !c.completada)
  if (filtroActivo.value === 'completadas') return citas.value.filter(c =>  c.completada)
  return citas.value  // 'todas'
})

// Cuenta cuantas citas pendientes hay para el badge del filtro
const contarPendientes = computed(() =>
  citas.value.filter(c => !c.completada).length
)

// =============================================================
// CARGA DE DATOS
// =============================================================
onMounted(async () => {
  await cargarCitas()
})

async function cargarCitas() {
  cargando.value = true
  try {
    // Carga TODAS las citas (el filtro se hace en el frontend con computed)
    const res = await citasAPI.obtenerTodas()
    // Ordena por fecha: la mas proxima primero
    citas.value = res.data.datos.sort((a, b) => 
      new Date(a.fecha) - new Date(b.fecha)
    )
  } catch (e) {
    error.value = 'No se pudieron cargar las citas. Verifica el servidor.'
  } finally {
    cargando.value = false
  }
}

// Cambia el filtro activo cuando el usuario hace click en los tabs
function cambiarFiltro(filtro) {
  filtroActivo.value = filtro
}

// =============================================================
// MODAL
// =============================================================
function abrirModalNuevo() {
  editando.value = false
  citaIdEditando.value = null
  errorModal.value = ''
  formulario.value = { doctor: '', especialidad: '', fecha: '', hora: '', lugar: '', notas: '' }
  mostrarModal.value = true
}

function abrirModalEditar(cita) {
  editando.value = true
  citaIdEditando.value = cita._id
  errorModal.value = ''
  formulario.value = {
    doctor:       cita.doctor,
    especialidad: cita.especialidad,
    fecha:        cita.fecha,
    hora:         cita.hora || '',
    lugar:        cita.lugar || '',
    notas:        cita.notas || ''
  }
  mostrarModal.value = true
}

function cerrarModal() {
  mostrarModal.value = false
  errorModal.value = ''
}

// =============================================================
// GUARDAR CITA
// =============================================================
async function guardarCita() {
  errorModal.value = ''
  guardando.value = true
  try {
    if (editando.value) {
      await citasAPI.actualizar(citaIdEditando.value, formulario.value)
      mostrarExito('Cita actualizada correctamente')
    } else {
      await citasAPI.crear(formulario.value)
      mostrarExito('Cita agendada correctamente')
    }
    cerrarModal()
    await cargarCitas()
  } catch (e) {
    errorModal.value = e.response?.data?.error || 'Error al guardar la cita'
  } finally {
    guardando.value = false
  }
}

// Alterna el estado completada/pendiente de una cita
async function toggleCompletada(cita) {
  try {
    await citasAPI.actualizar(cita._id, { completada: !cita.completada })
    cita.completada = !cita.completada   // Actualiza localmente sin recargar
    mostrarExito(cita.completada ? 'Cita marcada como completada' : 'Cita marcada como pendiente')
  } catch (e) {
    error.value = 'Error al actualizar el estado de la cita'
  }
}

function confirmarEliminar(cita) {
  citaAEliminar.value = cita
  mostrarConfirmacion.value = true
}

async function eliminarCita() {
  guardando.value = true
  try {
    await citasAPI.eliminar(citaAEliminar.value._id)
    mostrarConfirmacion.value = false
    mostrarExito('Cita eliminada')
    await cargarCitas()
  } catch (e) {
    error.value = 'Error al eliminar la cita'
  } finally {
    guardando.value = false
  }
}

// Formato legible de fecha para mostrar en la UI
function formatearFecha(fechaStr) {
  if (!fechaStr) return '-'
  const fecha = new Date(fechaStr + 'T00:00:00')
  return fecha.toLocaleDateString('es-GT', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  })
}

function mostrarExito(mensaje) {
  exito.value = mensaje
  setTimeout(() => { exito.value = '' }, 3000)
}
</script>

<style scoped>
.lista-citas {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cita-card {
  transition: var(--transicion);
}

/* Citas completadas se ven mas apagadas visualmente */
.cita-completada {
  opacity: 0.65;
}

.cita-icono {
  font-size: 1.8rem;
}

.cita-doctor {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-texto);
}

.cita-especialidad {
  font-size: 0.82rem;
  color: var(--color-acento);
  font-weight: 600;
}

.cita-detalles-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  background: var(--color-fondo);
  border-radius: 8px;
  padding: 12px;
}

.cita-detalle {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cita-detalle-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-texto-suave);
}

.cita-detalle-valor {
  font-size: 0.92rem;
  color: var(--color-texto);
}

/* Tabs de filtro */
.filtros-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background: white;
  padding: 6px;
  border-radius: 10px;
  width: fit-content;
  border: 1px solid var(--color-borde);
  box-shadow: var(--sombra-card);
}

.filtro-btn {
  padding: 7px 18px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: var(--color-texto-suave);
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.88rem;
  font-weight: 600;
  transition: var(--transicion);
  display: flex;
  align-items: center;
  gap: 6px;
}

.filtro-btn:hover {
  background: var(--color-primario-light);
  color: var(--color-primario-dark);
}

.filtro-btn.activo {
  background: var(--color-primario);
  color: white;
}

.filtro-count {
  background: rgba(255,255,255,0.3);
  border-radius: 20px;
  padding: 1px 7px;
  font-size: 0.78rem;
}

.filtro-btn.activo .filtro-count {
  background: rgba(255,255,255,0.25);
}

/* Toast notification - esquina superior derecha */
.toast {
  position: fixed;
  top: 24px;
  right: 28px;
  z-index: 999;
  padding: 13px 20px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 260px;
  max-width: 380px;
}
.toast-exito { background: #059669; color: white; }
.toast-error  { background: #DC2626; color: white; }

/* Animacion del toast */
.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastIn 0.2s ease reverse; }
@keyframes toastIn {
  from { opacity: 0; transform: translateX(30px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* Boton marcar pendiente - azul */
.btn-pendiente {
  background: var(--color-primario);
  color: white;
  border: none;
}
.btn-pendiente:hover {
  background: var(--color-primario-dark);
}
</style>
