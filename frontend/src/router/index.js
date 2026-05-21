// =============================================================
// ROUTER/INDEX.JS - Configuracion de Vue Router
// Define las rutas de la aplicacion (que componente se muestra
// segun la URL del navegador)
// =============================================================

import { createRouter, createWebHistory } from 'vue-router'

// Importacion lazy (dinamica): el componente se carga solo cuando
// el usuario navega a esa ruta. Mejora el rendimiento inicial.
const Dashboard  = () => import('../views/Dashboard.vue')
const Medicamentos = () => import('../views/Medicamentos.vue')
const Citas       = () => import('../views/Citas.vue')

// Definicion de las rutas
const routes = [
  {
    path: '/',              // URL raiz -> va al Dashboard
    name: 'dashboard',
    component: Dashboard,
    meta: { titulo: 'Inicio' }
  },
  {
    path: '/medicamentos',  // URL /medicamentos -> componente Medicamentos
    name: 'medicamentos',
    component: Medicamentos,
    meta: { titulo: 'Mis Medicamentos' }
  },
  {
    path: '/citas',         // URL /citas -> componente Citas
    name: 'citas',
    component: Citas,
    meta: { titulo: 'Mis Citas' }
  },
  {
    // Ruta catch-all: redirige cualquier URL desconocida al inicio
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  // createWebHistory: URLs limpias (sin el # de hash mode)
  // El servidor Nginx debe estar configurado para soportar esto (ya lo esta)
  history: createWebHistory(),
  routes
})

// Guard de navegacion: actualiza el titulo de la pagina al navegar
router.afterEach((to) => {
  document.title = `Vitalis - ${to.meta.titulo || 'App'}`
})

export default router
