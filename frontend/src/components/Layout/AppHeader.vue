<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <router-link to="/" class="logo">
          <span class="logo-icon">🍷</span>
          <span class="logo-text">{{ $t('app.title') }}</span>
        </router-link>
      </div>
      
      <nav class="header-nav">
        <router-link to="/" class="nav-link">
          {{ $t('nav.home') }}
        </router-link>
        <router-link to="/camera" class="nav-link">
          {{ $t('nav.camera') }}
        </router-link>
        <router-link to="/room" class="nav-link">
          {{ $t('nav.rooms') }}
        </router-link>
      </nav>
      
      <div class="header-right">
        <LanguageSelector />
        <UserMenu />
      </div>
    </div>
  </header>
</template>

<script>
import LanguageSelector from '@/components/Common/LanguageSelector.vue'
import UserMenu from '@/components/Common/UserMenu.vue'

export default {
  name: 'AppHeader',
  
  components: {
    LanguageSelector,
    UserMenu
  }
}
</script>

<style scoped>
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #333;
  font-weight: bold;
  font-size: 1.2rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.header-nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #007bff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }
  
  .header-nav {
    display: none;
  }
  
  .logo-text {
    display: none;
  }
}
</style>