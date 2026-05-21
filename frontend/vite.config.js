// =============================================================
// VITE.CONFIG.JS - Configuracion del bundler de Vue
// Vite es la herramienta que compila y empaqueta el proyecto Vue
// =============================================================

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // Plugin de Vue para que Vite entienda archivos .vue
  plugins: [vue()],
  
  // Configuracion del servidor de desarrollo local
  server: {
    host: '0.0.0.0',   // Necesario para que funcione dentro de Docker
    port: 3000          // Puerto del servidor de desarrollo
  }
})
