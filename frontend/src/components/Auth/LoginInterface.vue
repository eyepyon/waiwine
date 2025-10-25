<template>
  <div class="login-interface">
    <div class="login-container">
      <div class="login-header">
        <h1 class="app-title">{{ $t('app.title') }}</h1>
        <p class="app-subtitle">{{ $t('app.subtitle') }}</p>
      </div>
      
      <div class="login-form">
        <h2>{{ $t('auth.login') }}</h2>
        
        <!-- OAuth Provider Buttons -->
        <div class="oauth-providers">
          <button 
            v-for="provider in availableProviders"
            :key="provider.name"
            @click="loginWithProvider(provider.name)"
            :disabled="loading"
            :class="['oauth-btn', `oauth-${provider.name}`]"
          >
            <span class="provider-icon">{{ provider.icon }}</span>
            {{ $t('auth.login_with', { provider: provider.displayName }) }}
          </button>
        </div>
        
        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>{{ loadingMessage }}</p>
        </div>
        
        <!-- Error state -->
        <div v-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p class="error-message">{{ error }}</p>
          <button @click="clearError" class="clear-error-btn">
            {{ $t('common.close') }}
          </button>
        </div>
      </div>
      
      <!-- Language Selection for New Users -->
      <div v-if="showLanguageSelection" class="language-selection">
        <h3>{{ $t('auth.select_language') }}</h3>
        
        <div class="language-grid">
          <button
            v-for="language in availableLanguages"
            :key="language.code"
            @click="selectLanguage(language.code)"
            :class="['language-btn', { active: selectedLanguage === language.code }]"
          >
            <span class="language-flag">{{ language.flag }}</span>
            <span class="language-name">{{ language.name }}</span>
          </button>
        </div>
        
        <div class="language-actions">
          <button 
            @click="completeRegistration"
            :disabled="!selectedLanguage || registering"
            class="complete-registration-btn"
          >
            {{ registering ? $t('common.loading') : $t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { availableLanguages } from '@/i18n'

export default {
  name: 'LoginInterface',
  
  emits: ['login-success', 'login-error'],
  
  data() {
    return {
      loading: false,
      registering: false,
      error: null,
      loadingMessage: '',
      showLanguageSelection: false,
      selectedLanguage: null,
      tempUserData: null,
      availableLanguages,
      
      availableProviders: [
        {
          name: 'google',
          displayName: 'Google',
          icon: '🔍'
        },
        {
          name: 'twitter',
          displayName: 'X (Twitter)',
          icon: '🐦'
        },
        {
          name: 'line',
          displayName: 'LINE',
          icon: '💬'
        }
      ]
    }
  },
  
  methods: {
    async loginWithProvider(providerName) {
      this.loading = true
      this.error = null
      this.loadingMessage = this.$t('auth.login_with', { provider: this.getProviderDisplayName(providerName) })
      
      try {
        // Initiate OAuth flow
        const authUrl = await this.getAuthUrl(providerName)
        
        // Open OAuth popup or redirect
        const result = await this.handleOAuthFlow(authUrl, providerName)
        
        if (result.isNewUser) {
          // Show language selection for new users
          this.tempUserData = result.userData
          this.showLanguageSelection = true
          this.selectedLanguage = this.$i18n.locale // Default to current locale
        } else {
          // Existing user - complete login
          this.$emit('login-success', result.userData)
        }
        
      } catch (err) {
        console.error('Login error:', err)
        this.error = err.message || this.$t('auth.login_failed')
        this.$emit('login-error', err)
      } finally {
        this.loading = false
      }
    },
    
    async getAuthUrl(provider) {
      const response = await fetch('/api/auth/authorize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: provider,
          redirect_url: window.location.origin + '/auth/callback'
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to get ${provider} auth URL`)
      }
      
      const data = await response.json()
      return data.authorization_url
    },
    
    async handleOAuthFlow(authUrl, provider) {
      return new Promise((resolve, reject) => {
        // Open OAuth popup
        const popup = window.open(
          authUrl,
          `${provider}_oauth`,
          'width=500,height=600,scrollbars=yes,resizable=yes'
        )
        
        // Listen for OAuth callback
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed)
            reject(new Error('OAuth popup was closed'))
          }
        }, 1000)
        
        // Listen for OAuth success message
        const messageHandler = (event) => {
          if (event.origin !== window.location.origin) return
          
          if (event.data.type === 'oauth_success') {
            clearInterval(checkClosed)
            popup.close()
            window.removeEventListener('message', messageHandler)
            resolve(event.data.result)
          } else if (event.data.type === 'oauth_error') {
            clearInterval(checkClosed)
            popup.close()
            window.removeEventListener('message', messageHandler)
            reject(new Error(event.data.error))
          }
        }
        
        window.addEventListener('message', messageHandler)
      })
    },
    
    selectLanguage(languageCode) {
      this.selectedLanguage = languageCode
    },
    
    async completeRegistration() {
      if (!this.selectedLanguage || !this.tempUserData) return
      
      this.registering = true
      
      try {
        // Update user's language preference
        const response = await fetch('/api/user/language', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${this.tempUserData.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            language: this.selectedLanguage
          })
        })
        
        if (!response.ok) {
          throw new Error('Failed to update language preference')
        }
        
        // Update user data with new language
        this.tempUserData.user.main_language = this.selectedLanguage
        
        // Update app language
        this.$i18n.locale = this.selectedLanguage
        localStorage.setItem('user-language', this.selectedLanguage)
        
        this.$emit('login-success', this.tempUserData)
        
      } catch (err) {
        console.error('Registration error:', err)
        this.error = err.message || this.$t('auth.registration_failed')
      } finally {
        this.registering = false
      }
    },
    
    getProviderDisplayName(providerName) {
      const provider = this.availableProviders.find(p => p.name === providerName)
      return provider ? provider.displayName : providerName
    },
    
    clearError() {
      this.error = null
    }
  }
}
</script>

<style scoped>
.login-interface {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-container {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.app-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.app-subtitle {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.oauth-providers {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.oauth-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.oauth-btn:hover:not(:disabled) {
  border-color: #007bff;
  background: #f8f9fa;
}

.oauth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.oauth-google {
  border-color: #db4437;
}

.oauth-google:hover:not(:disabled) {
  border-color: #db4437;
  background: #fef7f7;
}

.oauth-twitter {
  border-color: #1da1f2;
}

.oauth-twitter:hover:not(:disabled) {
  border-color: #1da1f2;
  background: #f7fbff;
}

.oauth-line {
  border-color: #00b900;
}

.oauth-line:hover:not(:disabled) {
  border-color: #00b900;
  background: #f7fff7;
}

.provider-icon {
  font-size: 18px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 1rem;
  margin-top: 1rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.error-message {
  color: #e53e3e;
  margin-bottom: 1rem;
}

.clear-error-btn {
  padding: 6px 12px;
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.language-selection {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.language-selection h3 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
}

.language-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.language-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 0.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.language-btn:hover {
  border-color: #007bff;
}

.language-btn.active {
  border-color: #007bff;
  background: #f0f8ff;
}

.language-flag {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.language-name {
  font-size: 0.8rem;
  color: #333;
}

.language-actions {
  text-align: center;
}

.complete-registration-btn {
  padding: 12px 24px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.complete-registration-btn:hover:not(:disabled) {
  background: #218838;
}

.complete-registration-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .login-container {
    padding: 1.5rem;
  }
  
  .language-grid {
    grid-template-columns: 1fr;
  }
}
</style>