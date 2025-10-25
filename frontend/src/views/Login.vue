<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🍷</span>
          <span class="logo-text">{{ $t('app.title') }}</span>
        </div>
        
        <div class="language-selector-wrapper">
          <LanguageSelector />
        </div>
      </div>
      
      <div class="login-content">
        <div class="login-card">
          <div class="card-header">
            <h1 class="login-title">{{ $t('auth.login') }}</h1>
            <p class="login-subtitle">{{ $t('auth.login_subtitle') }}</p>
          </div>
          
          <LoginInterface />
          
          <div class="login-footer">
            <router-link to="/landing" class="back-link">
              ← {{ $t('common.back') }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoginInterface from '@/components/Auth/LoginInterface.vue'
import LanguageSelector from '@/components/Common/LanguageSelector.vue'

export default {
  name: 'LoginView',
  
  components: {
    LoginInterface,
    LanguageSelector
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.language-selector-wrapper {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.25rem;
  backdrop-filter: blur(10px);
}

.login-content {
  display: flex;
  justify-content: center;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  width: 100%;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
}

.back-link {
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.back-link:hover {
  color: #007bff;
}

@media (max-width: 480px) {
  .login-view {
    padding: 0.5rem;
  }
  
  .login-card {
    padding: 1.5rem;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
  
  .login-header {
    margin-bottom: 1.5rem;
  }
}
</style>
</template>