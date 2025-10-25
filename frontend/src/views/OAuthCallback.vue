<template>
  <div class="oauth-callback-view">
    <div class="callback-container">
      <div class="callback-content">
        <div class="loading-section">
          <div class="loading-spinner"></div>
          <h2 class="loading-title">{{ $t('auth.processing_login') }}</h2>
          <p class="loading-message">{{ loadingMessage }}</p>
        </div>
        
        <div v-if="error" class="error-section">
          <div class="error-icon">❌</div>
          <h2 class="error-title">{{ $t('auth.login_failed') }}</h2>
          <p class="error-message">{{ error }}</p>
          
          <div class="error-actions">
            <router-link to="/login" class="retry-btn">
              {{ $t('common.retry') }}
            </router-link>
            <router-link to="/landing" class="home-btn">
              {{ $t('nav.home') }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

export default {
  name: 'OAuthCallbackView',
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const { t } = useI18n()
    
    const loadingMessage = ref(t('auth.connecting_provider'))
    const error = ref('')
    
    const handleOAuthCallback = async () => {
      try {
        const { provider } = route.params
        const { code, state, error: oauthError } = route.query
        
        if (oauthError) {
          throw new Error(t('auth.oauth_error', { error: oauthError }))
        }
        
        if (!code) {
          throw new Error(t('auth.missing_auth_code'))
        }
        
        loadingMessage.value = t('auth.verifying_credentials')
        
        // Call the OAuth callback endpoint
        const response = await fetch(`/api/auth/oauth/${provider}/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            code,
            state
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || t('auth.login_failed'))
        }
        
        const authData = await response.json()
        
        loadingMessage.value = t('auth.completing_login')
        
        // Update auth store with the received data
        await authStore.setAuthData(authData)
        
        // Redirect to home page
        router.push({ name: 'Home' })
        
      } catch (err) {
        console.error('OAuth callback error:', err)
        error.value = err.message || t('auth.unknown_error')
      }
    }
    
    onMounted(() => {
      handleOAuthCallback()
    })
    
    return {
      loadingMessage,
      error
    }
  }
}
</script>

<style scoped>
.oauth-callback-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.callback-container {
  max-width: 500px;
  width: 100%;
}

.callback-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.loading-message {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.error-icon {
  font-size: 3rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #dc3545;
  margin: 0;
}

.error-message {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.retry-btn, .home-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.retry-btn {
  background: #007bff;
  color: white;
}

.retry-btn:hover {
  background: #0056b3;
}

.home-btn {
  background: #6c757d;
  color: white;
}

.home-btn:hover {
  background: #545b62;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .oauth-callback-view {
    padding: 1rem;
  }
  
  .callback-content {
    padding: 2rem 1.5rem;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .retry-btn, .home-btn {
    width: 100%;
  }
}
</style>
</template>