<template>
  <div class="landing-view">
    <header class="landing-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🍷</span>
          <span class="logo-text">{{ $t('app.title') }}</span>
        </div>
        
        <div class="header-actions">
          <LanguageSelector />
          <router-link to="/login" class="login-btn">
            {{ $t('auth.login') }}
          </router-link>
        </div>
      </div>
    </header>
    
    <main class="main-content">
      <div class="hero-section">
        <h1 class="hero-title">{{ $t('app.title') }}</h1>
        <p class="hero-subtitle">{{ $t('app.subtitle') }}</p>
        
        <div class="action-buttons">
          <router-link to="/room/guest-room" class="primary-btn">
            <span class="btn-icon">💬</span>
            {{ $t('landing.try_as_guest') }}
          </router-link>
          
          <router-link to="/login" class="secondary-btn">
            <span class="btn-icon">🚀</span>
            {{ $t('landing.get_started') }}
          </router-link>
          
          <button @click="scrollToFeatures" class="tertiary-btn">
            <span class="btn-icon">ℹ️</span>
            {{ $t('landing.learn_more') }}
          </button>
        </div>
      </div>
      
      <div ref="featuresSection" class="features-section">
        <h2 class="features-title">{{ $t('landing.features_title') }}</h2>
        
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🍷</div>
            <h3>{{ $t('wine.recognition') }}</h3>
            <p>{{ $t('wine.recognition_description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">👥</div>
            <h3>{{ $t('room.video_chat') }}</h3>
            <p>{{ $t('room.video_chat_description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <h3>{{ $t('translation.real_time') }}</h3>
            <p>{{ $t('translation.real_time_description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🔐</div>
            <h3>{{ $t('auth.social_login') }}</h3>
            <p>{{ $t('auth.social_login_description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>{{ $t('landing.mobile_friendly') }}</h3>
            <p>{{ $t('landing.mobile_friendly_description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>{{ $t('landing.instant_matching') }}</h3>
            <p>{{ $t('landing.instant_matching_description') }}</p>
          </div>
        </div>
      </div>
      
      <div class="cta-section">
        <h2 class="cta-title">{{ $t('landing.ready_to_start') }}</h2>
        <p class="cta-subtitle">{{ $t('landing.join_community') }}</p>
        
        <router-link to="/login" class="cta-btn">
          <span class="btn-icon">🍷</span>
          {{ $t('landing.start_wine_journey') }}
        </router-link>
      </div>
    </main>
    
    <footer class="landing-footer">
      <div class="footer-content">
        <div class="footer-logo">
          <span class="logo-icon">🍷</span>
          <span class="logo-text">{{ $t('app.title') }}</span>
        </div>
        
        <div class="footer-links">
          <a href="#" class="footer-link">{{ $t('footer.privacy') }}</a>
          <a href="#" class="footer-link">{{ $t('footer.terms') }}</a>
          <a href="#" class="footer-link">{{ $t('footer.support') }}</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import LanguageSelector from '@/components/Common/LanguageSelector.vue'

export default {
  name: 'LandingView',
  
  components: {
    LanguageSelector
  },
  
  methods: {
    scrollToFeatures() {
      this.$refs.featuresSection.scrollIntoView({ 
        behavior: 'smooth' 
      })
    }
  }
}
</script>

<style scoped>
.landing-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Header */
.landing-header {
  background: rgba(255, 255, 255, 0.1);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.login-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

/* Main Content */
.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  color: white;
  margin-bottom: 6rem;
  padding: 4rem 0;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 3rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn, .secondary-btn, .tertiary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: none;
  cursor: pointer;
}

.primary-btn {
  background: #28a745;
  color: white;
}

.primary-btn:hover {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.secondary-btn {
  background: #007bff;
  color: white;
}

.secondary-btn:hover {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.tertiary-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.tertiary-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 1.3rem;
}

/* Features Section */
.features-section {
  margin-bottom: 6rem;
}

.features-title {
  text-align: center;
  color: white;
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 3rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* CTA Section */
.cta-section {
  text-align: center;
  color: white;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  margin-bottom: 4rem;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.cta-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #28a745;
  color: white;
  padding: 1.2rem 2.5rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.cta-btn:hover {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

/* Footer */
.landing-footer {
  background: rgba(0, 0, 0, 0.2);
  color: white;
  padding: 2rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
}

.footer-links {
  display: flex;
  gap: 2rem;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: white;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-btn, .secondary-btn, .tertiary-btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .features-title {
    font-size: 2rem;
  }
  
  .cta-title {
    font-size: 2rem;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>