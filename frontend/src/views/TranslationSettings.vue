<template>
  <MainLayout>
    <div class="translation-settings-view">
      <div class="settings-header">
        <router-link to="/settings" class="back-link">
          <i class="fas fa-arrow-left"></i>
          {{ $t('common.back') }}
        </router-link>
        <h1 class="page-title">{{ $t('translation.settings_title') }}</h1>
        <p class="page-subtitle">{{ $t('translation.settings_description') }}</p>
      </div>
      
      <TranslationSettings />
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '@/components/Layout/MainLayout.vue'
import TranslationSettings from '@/components/Translation/TranslationSettings.vue'

export default {
  name: 'TranslationSettingsView',
  components: {
    MainLayout,
    TranslationSettings
  }
}
</script>

<style scoped>
.translation-settings-view {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 2rem;
}

.settings-header {
  max-width: 800px;
  margin: 0 auto 2rem auto;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 1rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #007bff;
  text-decoration: none;
}

.page-title {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 2rem;
}

.page-subtitle {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .translation-settings-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}
</style>