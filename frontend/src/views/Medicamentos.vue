<template>
  <!--
    MEDICAMENTOS.VUE - Vista de gestion de medicamentos
    Permite al usuario ver, agregar, editar y eliminar medicamentos.
    Toda la comunicacion con la base de datos pasa por el backend Flask.
  -->
  <div>

    <!-- Cabecera con titulo y boton para agregar -->
    <div class="page-header flex items-center justify-between">
      <div>
        <h2>Mis Medicamentos</h2>
        <p>Gestiona tus medicamentos y dosis diarias</p>
      </div>
      <!-- Al hacer click abre el modal de nuevo medicamento -->
      <button class="btn btn-primario" @click="abrirModalNuevo">
        <span>+</span> Agregar Medicamento
      </button>
    </div>

    <!-- Toast notifications -->
    <transition name="toast">
      <div v-if="exito" class="toast toast-exito">✓ {{ exito }}</div>
    </transition>
    <transition name="toast">
      <div v-if="error" class="toast toast-error">⚠ {{ error }}</div>
    </transition>

    <!-- Spinner de carga -->
    <div v-if="cargando" class="spinner"></div>

    <!-- Estado vacio: no hay medicamentos registrados -->
    <div v-else-if="medicamentos.length === 0" class="card estado-vacio">
      <div class="icono-grande">💊</div>
      <h3>Sin medicamentos registrados</h3>
      <p>Agrega tu primer medicamento usando el boton de arriba</p>
    </div>

    <!-- Grid de cards de medicamentos -->
    <div v-else class="cards-grid">
      <div 
        v-for="med in medicamentos" 
        :key="med._id"
        class="card medicamento-card"
      >
        <!-- Encabezado de la card: nombre y estado -->
        <div class="flex items-center justify-between" style="margin-bottom: 14px;">
          <div class="flex items-center gap-2">
            <span style="font-size: 1.5rem;">💊</span>
            <h3 class="med-nombre">{{ med.nombre }}</h3>
          </div>
          <!-- badge-activo si activo=true, badge-inactivo si false -->
          <span :class="['badge', med.activo ? 'badge-activo' : 'badge-inactivo']">
            {{ med.activo ? 'Activo' : 'Inactivo' }}
          </span>
        </div>

        <!-- Detalles del medicamento -->
        <div class="med-detalles">
          <div class="med-detalle-item">
            <span class="med-detalle-label">Dosis</span>
            <span class="med-detalle-valor">{{ med.dosis }}</span>
          </div>
          <div class="med-detalle-item">
            <span class="med-detalle-label">Frecuencia</span>
            <span class="med-detalle-valor">{{ med.frecuencia }}</span>
          </div>
          <div v-if="med.indicaciones" class="med-detalle-item">
            <span class="med-detalle-label">Indicaciones</span>
            <span class="med-detalle-valor">{{ med.indicaciones }}</span>
          </div>
        </div>

        <!-- Acciones: editar y eliminar -->
        <div class="flex gap-2" style="margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--color-borde);">
          <button class="btn btn-secundario btn-sm" @click="abrirModalEditar(med)">
            Editar
          </button>
          <button 
            :class="['btn', 'btn-sm', med.activo ? 'btn-neutro' : 'btn-exito']"
            @click="toggleActivo(med)"
            style="flex: 1;"
          >
            {{ med.activo ? 'Desactivar' : 'Activar' }}
          </button>
          <button class="btn btn-peligro btn-sm" @click="confirmarEliminar(med)">
            Eliminar
          </button>
        </div>

      </div>
    </div>


    <!-- =======================================================
         MODAL: Formulario para agregar o editar medicamento
         v-if controla si el modal se muestra o no
         ======================================================= -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <!--
        @click.self = el click en el overlay (fondo) cierra el modal
        pero no cierra si el click fue dentro del .modal
      -->
      <div class="modal">

        <div class="modal-header">
          <h3>{{ editando ? 'Editar Medicamento' : 'Nuevo Medicamento' }}</h3>
          <button class="btn-cerrar" @click="cerrarModal">×</button>
        </div>

        <!-- Formulario: v-model enlaza el valor del input con la variable reactiva -->
        <form @submit.prevent="guardarMedicamento">

          <div class="form-grupo">
            <label>Nombre del medicamento *</label>
            <input 
              v-model="formulario.nombre"
              type="text"
              placeholder="Ej: Losartan 50mg"
              required
            />
          </div>

          <div class="form-grupo">
            <label>Dosis por toma *</label>
            <input 
              v-model="formulario.dosis"
              type="text"
              placeholder="Ej: 1 tableta, 5ml, 2 capsulas"
              required
            />
          </div>

          <div class="form-grupo">
            <label>Frecuencia *</label>
            <input 
              v-model="formulario.frecuencia"
              type="text"
              placeholder="Ej: Cada 8 horas, Una vez al dia en la noche"
              required
            />
          </div>

          <div class="form-grupo">
            <label>Indicaciones adicionales</label>
            <textarea 
              v-model="formulario.indicaciones"
              placeholder="Ej: Tomar con alimentos, no suspender sin consultar al medico..."
            ></textarea>
          </div>

          <!-- Mensaje de error dentro del modal -->
          <div v-if="errorModal" class="alerta alerta-error">{{ errorModal }}</div>

          <div class="form-acciones">
            <button type="button" class="btn btn-secundario" @click="cerrarModal">
              Cancelar
            </button>
            <button type="submit" class="btn btn-primario" :disabled="guardando">
              {{ guardando ? 'Guardando...' : (editando ? 'Actualizar' : 'Guardar') }}
            </button>
          </div>

        </form>
      </div>
    </div>


    <!-- Modal de confirmacion para eliminar -->
    <div v-if="mostrarConfirmacion" class="modal-overlay" @click.self="mostrarConfirmacion = false">
      <div class="modal" style="max-width: 400px;">
        <div class="modal-header">
          <h3>Confirmar eliminacion</h3>
          <button class="btn-cerrar" @click="mostrarConfirmacion = false">×</button>
        </div>
        <p style="color: var(--color-texto-suave); margin-bottom: 20px;">
          Esta accion eliminara permanentemente <strong>{{ medicamentoAEliminar?.nombre }}</strong>.
          No se puede deshacer.
        </p>
        <div class="form-acciones">
          <button class="btn btn-secundario" @click="mostrarConfirmacion = false">Cancelar</button>
          <button class="btn btn-peligro" @click="eliminarMedicamento" :disabled="guardando">
            {{ guardando ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { medicamentosAPI } from '../services/api.js'

// =============================================================
// ESTADO REACTIVO
// =============================================================
const medicamentos    = ref([])   // Lista obtenida del backend
const cargando        = ref(true) // Estado de carga inicial
const guardando       = ref(false)// Estado durante submit
const mostrarModal    = ref(false) // Controla visibilidad del modal
const mostrarConfirmacion = ref(false)
const editando        = ref(false) // true = editar, false = nuevo
const error           = ref('')   // Mensaje de error global
const exito           = ref('')   // Mensaje de exito temporal
const errorModal      = ref('')   // Error dentro del modal
const medicamentoAEliminar = ref(null)
const medIdEditando   = ref(null) // ID del medicamento en edicion

// Objeto del formulario: se llena al abrir el modal
const formulario = ref({
  nombre: '',
  dosis: '',
  frecuencia: '',
  indicaciones: ''
})

// =============================================================
// CARGA INICIAL DE DATOS
// =============================================================
onMounted(async () => {
  await cargarMedicamentos()
})

// Funcion reutilizable para recargar la lista del servidor
async function cargarMedicamentos() {
  cargando.value = true
  try {
    const res = await medicamentosAPI.obtenerTodos()
    medicamentos.value = res.data.datos   // Extrae el array del objeto respuesta
  } catch (e) {
    error.value = 'No se pudieron cargar los medicamentos. Verifica el servidor.'
  } finally {
    cargando.value = false
  }
}

// =============================================================
// FUNCIONES DEL MODAL
// =============================================================

// Abre el modal para AGREGAR (resetea el formulario)
function abrirModalNuevo() {
  editando.value = false
  medIdEditando.value = null
  errorModal.value = ''
  formulario.value = { nombre: '', dosis: '', frecuencia: '', indicaciones: '' }
  mostrarModal.value = true
}

// Abre el modal para EDITAR (rellena el formulario con datos existentes)
function abrirModalEditar(med) {
  editando.value = true
  medIdEditando.value = med._id   // Guarda el ID para el PUT
  errorModal.value = ''
  // Copia los datos del medicamento al formulario
  formulario.value = {
    nombre:       med.nombre,
    dosis:        med.dosis,
    frecuencia:   med.frecuencia,
    indicaciones: med.indicaciones || ''
  }
  mostrarModal.value = true
}

function cerrarModal() {
  mostrarModal.value = false
  errorModal.value = ''
}

// =============================================================
// GUARDAR (crear o actualizar)
// =============================================================
async function guardarMedicamento() {
  errorModal.value = ''
  guardando.value = true

  try {
    if (editando.value) {
      // Si estamos editando, hace PUT con el ID guardado
      await medicamentosAPI.actualizar(medIdEditando.value, formulario.value)
      mostrarExito('Medicamento actualizado correctamente')
    } else {
      // Si es nuevo, hace POST
      await medicamentosAPI.crear(formulario.value)
      mostrarExito('Medicamento agregado correctamente')
    }
    cerrarModal()
    await cargarMedicamentos()   // Recarga la lista actualizada

  } catch (e) {
    // Muestra el mensaje de error que devolvio el backend
    errorModal.value = e.response?.data?.error || 'Error al guardar. Intenta de nuevo.'
  } finally {
    guardando.value = false
  }
}

// Activa o desactiva un medicamento sin abrir el modal
async function toggleActivo(med) {
  try {
    await medicamentosAPI.actualizar(med._id, { activo: !med.activo })
    // Actualiza localmente sin recargar todo (mas rapido)
    med.activo = !med.activo
    mostrarExito(med.activo ? 'Medicamento activado' : 'Medicamento desactivado')
  } catch (e) {
    error.value = 'Error al actualizar el estado'
  }
}

// Muestra el modal de confirmacion antes de eliminar
function confirmarEliminar(med) {
  medicamentoAEliminar.value = med
  mostrarConfirmacion.value = true
}

// Ejecuta la eliminacion real tras confirmar
async function eliminarMedicamento() {
  guardando.value = true
  try {
    await medicamentosAPI.eliminar(medicamentoAEliminar.value._id)
    mostrarConfirmacion.value = false
    mostrarExito('Medicamento eliminado')
    await cargarMedicamentos()   // Recarga la lista
  } catch (e) {
    error.value = 'Error al eliminar el medicamento'
  } finally {
    guardando.value = false
  }
}

// Muestra un mensaje de exito por 3 segundos y luego lo oculta
function mostrarExito(mensaje) {
  exito.value = mensaje
  setTimeout(() => { exito.value = '' }, 3000)
}
</script>

<style scoped>
.medicamento-card { transition: var(--transicion); }

.med-nombre {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-texto);
}

.med-detalles {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--color-fondo);
  border-radius: 8px;
  padding: 12px;
}

.med-detalle-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.med-detalle-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-texto-suave);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.med-detalle-valor {
  font-size: 0.92rem;
  color: var(--color-texto);
}

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
  min-width: 260px;
}
.toast-exito { background: #059669; color: white; }
.toast-error  { background: #DC2626; color: white; }
.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastIn 0.2s ease reverse; }
@keyframes toastIn {
  from { opacity: 0; transform: translateX(30px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
