<template>
  <div class="oauth-callback">
    <div class="callback-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <h2>{{ $t('auth.processing') }}</h2>
        <p>{{ $t('auth.completing_login') }}</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">❌</div>
        <h2>{{ $t('auth.login_failed') }}</h2>
        <p class="error-message">{{ error }}</p>
        <button @click="retryLogin" class="retry-btn">
          {{ $t('auth.try_again') }}
        </button>
      </div>
      
      <div v-else class="success-state">
        <div class="success-icon">✅</div>
        <h2>{{ $t('auth.login_successful') }}</h2>
        <p>{{ $t('auth.redirecting') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'OAuthCallback',
  
  data() {
    return {
      loading: true,
      error: null
    }
  },
  
  async mounted() {
    await this.handleCallback()
  },
  
  methods: {
    async handleCallback() {
      try {
        this.loading = true
        this.error = null
        
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')
        const error = urlParams.get('error')
        const provider = this.$route.params.provider
        
        if (error) {
          throw new Error(`OAuth error: ${error}`)
        }
        
        if (!code || !state) {
          throw new Error('Missing authorization code or state')
        }
        
        // Exchange code for token
        const response = await fetch(`/api/auth/${provider}/callback?code=${code}&state=${state}`)
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Authentication failed')
        }
        
        const result = await response.json()
        
        if (!result.success) {
          throw new Error(result.error || 'Authentication failed')
        }
        
        // Check if this is a popup callback
        if (window.opener) {
          // Send result to parent window
          window.opener.postMessage({
            type: 'oauth_success',
            result: {
              userData: result.user,
              token: result.token,
              isNewUser: !result.user.main_language || result.user.main_language === 'ja'
            }
          }, window.location.origin)
          
          window.close()
          return
        }
        
        // Handle direct callback (not popup)
        const authStore = useAuthStore()
        
        // Check if user needs to select language (new user)
        if (!result.user.main_language || result.user.main_language === 'ja') {
          // Redirect to language selection
          this.$router.push({
            name: 'LanguageSelection',
            query: {
              token: result.token,
              user: JSON.stringify(result.user)
            }
          })
        } else {
          // Complete login
          await authStore.login(result.user, result.token)
          
          // Redirect to intended page or home
          const redirectUrl = result.redirect_url || '/'
          this.$router.push(redirectUrl)
        }
        
      } catch (err) {
        console.error('OAuth callback error:', err)
        this.error = err.message
        
        // Send error to parent window if popup
        if (window.opener) {
          window.opener.postMessage({
            type: 'oauth_error',
            error: err.message
          }, window.location.origin)
          
          window.close()
        }
      } finally {
        this.loading = false
      }
    },
    
    retryLogin() {
      // Close popup or redirect to login
      if (window.opener) {
        window.close()
      } else {
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style scoped>
.oauth-callback {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.callback-container {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.loading-state h2,
.error-state h2,
.success-state h2 {
  margin: 1rem 0 0.5rem 0;
  color: #333;
}

.loading-state p,
.error-state p,
.success-state p {
  color: #666;
  margin-bottom: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #e53e3e;
  font-weight: 500;
}

.retry-btn {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #0056b3;
}

@media (max-width: 480px) {
  .callback-container {
    padding: 2rem 1.5rem;
  }
}
</style>