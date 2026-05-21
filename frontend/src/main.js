// =============================================================
// MAIN.JS - Punto de entrada principal de la aplicacion Vue
// Aqui se crea la instancia de Vue, se registra el router
// y se monta la aplicacion en el elemento #app del HTML
// =============================================================

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Importa los estilos globales de la aplicacion
import './assets/styles.css'

// Crea la aplicacion Vue y le inyecta el router, luego la monta
// en el div con id="app" que esta en index.html
createApp(App)
  .use(router)
  .mount('#app')
