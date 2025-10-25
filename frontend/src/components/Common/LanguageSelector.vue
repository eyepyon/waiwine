<template>
  <div class="language-selector">
    <button 
      @click="toggleDropdown"
      class="language-btn"
      :class="{ active: showDropdown, loading: loading }"
      :disabled="loading"
    >
      <div v-if="loading" class="loading-spinner"></div>
      <template v-else>
        <span class="current-flag">{{ currentLanguage.flag }}</span>
        <span class="current-name">{{ currentLanguage.name }}</span>
        <span class="dropdown-arrow">▼</span>
      </template>
    </button>
    
    <div v-if="showDropdown" class="language-dropdown">
      <button
        v-for="language in availableLanguages"
        :key="language.code"
        @click="selectLanguage(language.code)"
        :class="['language-option', { active: language.code === currentLanguage.code }]"
        :disabled="loading"
      >
        <span class="language-flag">{{ language.flag }}</span>
        <span class="language-name">{{ language.name }}</span>
        <span v-if="language.code === currentLanguage.code" class="check-mark">✓</span>
      </button>
    </div>
    
    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Backdrop to close dropdown -->
    <div 
      v-if="showDropdown" 
      class="dropdown-backdrop"
      @click="closeDropdown"
    ></div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useLanguage } from '@/composables/useLanguage'

export default {
  name: 'LanguageSelector',
  
  setup() {
    const showDropdown = ref(false)
    const {
      loading,
      error,
      currentLanguage,
      availableLanguages,
      changeLanguage
    } = useLanguage()
    
    let clickOutsideHandler = null
    
    const toggleDropdown = () => {
      showDropdown.value = !showDropdown.value
    }
    
    const closeDropdown = () => {
      showDropdown.value = false
    }
    
    const selectLanguage = async (languageCode) => {
      if (languageCode === currentLanguage.value.code) {
        closeDropdown()
        return
      }
      
      try {
        await changeLanguage(languageCode)
        closeDropdown()
      } catch (err) {
        console.error('Failed to change language:', err)
        // Error is already handled in the composable
        closeDropdown()
      }
    }
    
    onMounted(() => {
      // Close dropdown when clicking outside
      clickOutsideHandler = (event) => {
        const element = document.querySelector('.language-selector')
        if (element && !element.contains(event.target)) {
          closeDropdown()
        }
      }
      document.addEventListener('click', clickOutsideHandler)
    })
    
    onUnmounted(() => {
      if (clickOutsideHandler) {
        document.removeEventListener('click', clickOutsideHandler)
      }
    })
    
    return {
      showDropdown,
      loading,
      error,
      currentLanguage,
      availableLanguages,
      toggleDropdown,
      closeDropdown,
      selectLanguage
    }
  }
}
</script>

<style scoped>
.language-selector {
  position: relative;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  min-width: 120px;
  justify-content: center;
}

.language-btn:hover,
.language-btn.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.language-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.language-btn.loading {
  background: rgba(255, 255, 255, 0.15);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.current-flag {
  font-size: 1.1rem;
}

.current-name {
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.2s ease;
}

.language-btn.active .dropdown-arrow {
  transform: rotate(180deg);
}

.language-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 180px;
  max-height: 300px;
  overflow-y: auto;
}

.language-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
  position: relative;
}

.language-option:hover:not(:disabled) {
  background: #f8f9fa;
}

.language-option.active {
  background: #e3f2fd;
  color: #1976d2;
}

.language-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.language-option:first-child {
  border-radius: 8px 8px 0 0;
}

.language-option:last-child {
  border-radius: 0 0 8px 8px;
}

.language-flag {
  font-size: 1.1rem;
}

.language-name {
  font-weight: 500;
  flex: 1;
}

.check-mark {
  color: #1976d2;
  font-weight: bold;
  font-size: 0.9rem;
}

.error-message {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  font-size: 0.8rem;
  z-index: 1001;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dropdown-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

@media (max-width: 768px) {
  .current-name {
    display: none;
  }
  
  .language-btn {
    min-width: 60px;
  }
  
  .language-dropdown {
    right: -1rem;
    min-width: 160px;
  }
  
  .error-message {
    right: -1rem;
    max-width: 200px;
    white-space: normal;
  }
}
</style>