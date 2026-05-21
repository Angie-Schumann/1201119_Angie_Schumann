<template>
  <!-- 
    APP.VUE - Componente raiz de la aplicacion
    Define el layout principal: sidebar fijo + contenido dinamico.
    <router-view> es donde Vue renderiza el componente de la ruta activa.
  -->
  <div class="app-layout">

    <!-- Barra de navegacion lateral -->
    <aside class="sidebar">

      <!-- Logo y nombre de la app -->
      <div class="sidebar-logo">
        <h1>Vitalis</h1>
        
      </div>

      <!-- Links de navegacion -->
      <nav class="sidebar-nav">

        <!-- router-link: componente de Vue Router para navegar sin recargar la pagina -->
        <!-- :class="{ activo: $route.path === '/' }" aplica la clase "activo" segun la URL actual -->
        <router-link 
          to="/" 
          class="nav-link"
          :class="{ activo: $route.path === '/' }"
        >
          <span class="icono">🏠</span>
          Inicio
        </router-link>

        <router-link 
          to="/medicamentos" 
          class="nav-link"
          :class="{ activo: $route.path === '/medicamentos' }"
        >
          <span class="icono">💊</span>
          Medicamentos
        </router-link>

        <router-link 
          to="/citas" 
          class="nav-link"
          :class="{ activo: $route.path === '/citas' }"
        >
          <span class="icono">📅</span>
          Citas Medicas
        </router-link>

      </nav>

    </aside>

    <!-- Contenido principal: cambia segun la ruta activa -->
    <main class="main-content">
      <!-- Transicion animada entre paginas -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

  </div>
</template>

<script setup>
// App.vue es un componente de presentacion puro.
// No necesita logica adicional; Vue Router y los componentes hijos
// se encargan de todo el estado y las peticiones al backend.
</script>
