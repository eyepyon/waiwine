import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { useAuthStore } from './stores/auth'
import { useLanguage } from './composables/useLanguage'

// Create Vue app
const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)
app.use(i18n)

// Initialize stores and language system
async function initializeApp() {
  const authStore = useAuthStore()
  const { initializeLanguage } = useLanguage()
  
  // Initialize auth store first
  await authStore.initialize()
  
  // Then initialize language based on user preferences
  initializeLanguage()
}

// Initialize and mount app
initializeApp().then(() => {
  app.mount('#app')
}).catch(error => {
  console.error('Failed to initialize app:', error)
  // Mount anyway with default settings
  app.mount('#app')
})