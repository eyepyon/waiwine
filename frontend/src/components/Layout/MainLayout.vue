<template>
  <div class="main-layout">
    <AppHeader />
    
    <main class="main-content">
      <div class="content-container">
        <slot />
      </div>
    </main>
    
    <!-- Mobile Navigation -->
    <nav v-if="isMobile" class="mobile-nav">
      <router-link to="/" class="mobile-nav-item" :class="{ active: $route.name === 'Home' }">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">{{ $t('nav.home') }}</span>
      </router-link>
      
      <router-link to="/camera" class="mobile-nav-item" :class="{ active: $route.name === 'Camera' }">
        <span class="nav-icon">📷</span>
        <span class="nav-label">{{ $t('nav.camera') }}</span>
      </router-link>
      
      <router-link to="/rooms" class="mobile-nav-item" :class="{ active: $route.name === 'Rooms' }">
        <span class="nav-icon">🎥</span>
        <span class="nav-label">{{ $t('nav.rooms') }}</span>
      </router-link>
      
      <router-link to="/settings" class="mobile-nav-item" :class="{ active: $route.name === 'Settings' }">
        <span class="nav-icon">⚙️</span>
        <span class="nav-label">{{ $t('nav.settings') }}</span>
      </router-link>
    </nav>
    
    <!-- Loading overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner large"></div>
        <p class="loading-text">{{ loadingMessage || $t('common.loading') }}</p>
      </div>
    </div>
    
    <!-- Toast notifications -->
    <div class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="removeToast(toast.id)"
      >
        <span class="toast-icon">{{ getToastIcon(toast.type) }}</span>
        <span class="toast-message">{{ toast.message }}</span>
        <button class="toast-close" @click.stop="removeToast(toast.id)">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppHeader from './AppHeader.vue'

export default {
  name: 'MainLayout',
  
  components: {
    AppHeader
  },
  
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    loadingMessage: {
      type: String,
      default: ''
    }
  },
  
  setup() {
    const windowWidth = ref(window.innerWidth)
    const toasts = ref([])
    
    const isMobile = computed(() => windowWidth.value <= 768)
    
    const isLoading = computed(() => {
      // You can extend this to check global loading state
      return false
    })
    
    const handleResize = () => {
      windowWidth.value = window.innerWidth
    }
    
    const addToast = (message, type = 'info', duration = 5000) => {
      const id = Date.now() + Math.random()
      const toast = { id, message, type }
      
      toasts.value.push(toast)
      
      if (duration > 0) {
        setTimeout(() => {
          removeToast(id)
        }, duration)
      }
      
      return id
    }
    
    const removeToast = (id) => {
      const index = toasts.value.findIndex(toast => toast.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }
    
    const getToastIcon = (type) => {
      const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
      }
      return icons[type] || icons.info
    }
    
    onMounted(() => {
      window.addEventListener('resize', handleResize)
      
      // Global toast event listener
      window.addEventListener('show-toast', (event) => {
        const { message, type, duration } = event.detail
        addToast(message, type, duration)
      })
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('show-toast', () => {})
    })
    
    // Expose methods for child components
    window.showToast = (message, type = 'info', duration = 5000) => {
      addToast(message, type, duration)
    }
    
    return {
      isMobile,
      isLoading,
      toasts,
      addToast,
      removeToast,
      getToastIcon
    }
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px; /* Space for mobile nav */
}

.content-container {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
}

/* Mobile Navigation */
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-around;
  padding: 0.5rem 0;
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  text-decoration: none;
  color: #666;
  transition: color 0.2s ease;
  min-width: 60px;
}

.mobile-nav-item.active,
.mobile-nav-item:hover {
  color: #007bff;
}

.nav-icon {
  font-size: 1.2rem;
}

.nav-label {
  font-size: 0.7rem;
  font-weight: 500;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 2rem;
}

.loading-spinner.large {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-text {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 80px;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideIn 0.3s ease;
}

.toast:hover {
  transform: translateX(-4px);
}

.toast-success {
  border-left-color: #28a745;
  background: #f8fff9;
}

.toast-error {
  border-left-color: #dc3545;
  background: #fff8f8;
}

.toast-warning {
  border-left-color: #ffc107;
  background: #fffdf5;
}

.toast-info {
  border-left-color: #17a2b8;
  background: #f8fdff;
}

.toast-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.toast-close:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #666;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Desktop styles */
@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
  
  .main-content {
    padding-bottom: 0;
  }
  
  .content-container {
    padding: 2rem;
  }
}

/* Mobile styles */
@media (max-width: 768px) {
  .main-layout {
    height: 100vh;
    overflow: hidden;
  }
  
  .main-content {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 90px; /* Increased space for mobile nav */
  }
  
  .content-container {
    padding: 1rem 0.75rem;
    min-height: calc(100vh - 140px);
  }
  
  .mobile-nav {
    padding: 0.75rem 0 calc(0.75rem + env(safe-area-inset-bottom));
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(0, 0, 0, 0.1);
  }
  
  .mobile-nav-item {
    padding: 0.75rem 0.5rem;
    border-radius: 8px;
    transition: all 0.2s ease;
    min-height: 44px;
    justify-content: center;
  }
  
  .mobile-nav-item:active {
    background: rgba(0, 123, 255, 0.1);
    transform: scale(0.95);
  }
  
  .nav-icon {
    font-size: 1.4rem;
  }
  
  .nav-label {
    font-size: 0.75rem;
    font-weight: 600;
  }
  
  .toast-container {
    right: 0.5rem;
    left: 0.5rem;
    top: 60px;
    max-width: none;
  }
  
  .toast {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .toast-message {
    font-size: 0.85rem;
    line-height: 1.3;
  }
  
  .loading-overlay {
    background: rgba(255, 255, 255, 0.95);
  }
  
  .loading-content {
    padding: 1.5rem;
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  .mobile-nav-item {
    touch-action: manipulation;
  }
  
  .toast {
    touch-action: manipulation;
  }
  
  .toast-close {
    min-width: 44px;
    min-height: 44px;
  }
}

/* Landscape orientation on mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .mobile-nav {
    padding: 0.5rem 0 calc(0.5rem + env(safe-area-inset-bottom));
  }
  
  .mobile-nav-item {
    padding: 0.5rem;
  }
  
  .nav-icon {
    font-size: 1.2rem;
  }
  
  .nav-label {
    font-size: 0.7rem;
  }
  
  .main-content {
    padding-bottom: 70px;
  }
  
  .content-container {
    min-height: calc(100vh - 110px);
  }
}

/* Very small screens */
@media (max-width: 360px) {
  .content-container {
    padding: 0.75rem 0.5rem;
  }
  
  .mobile-nav-item {
    min-width: 50px;
  }
  
  .nav-label {
    font-size: 0.7rem;
  }
}
</style>
</template>