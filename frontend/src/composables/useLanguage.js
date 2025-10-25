/**
 * Composable for language management and switching
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { availableLanguages } from '@/i18n'

export function useLanguage() {
  const { locale } = useI18n()
  
  const loading = ref(false)
  const error = ref(null)
  
  // Current language info
  const currentLanguage = computed(() => {
    return availableLanguages.find(lang => lang.code === locale.value) || availableLanguages[0]
  })
  
  // Check if language is supported
  const isLanguageSupported = (languageCode) => {
    return availableLanguages.some(lang => lang.code === languageCode)
  }
  
  // Get browser language preference
  const getBrowserLanguage = () => {
    const browserLang = navigator.language.split('-')[0]
    return isLanguageSupported(browserLang) ? browserLang : 'ja'
  }
  
  // Get stored language preference
  const getStoredLanguage = () => {
    const stored = localStorage.getItem('user-language')
    return stored && isLanguageSupported(stored) ? stored : null
  }
  
  // Initialize language from various sources
  const initializeLanguage = (userLanguage = null) => {
    let targetLanguage = 'ja' // default
    
    // Priority: User profile > localStorage > browser > default
    if (userLanguage) {
      targetLanguage = userLanguage
    } else {
      const stored = getStoredLanguage()
      if (stored) {
        targetLanguage = stored
      } else {
        targetLanguage = getBrowserLanguage()
      }
    }
    
    if (locale.value !== targetLanguage) {
      locale.value = targetLanguage
      localStorage.setItem('user-language', targetLanguage)
    }
  }
  
  // Change language
  const changeLanguage = async (languageCode, updateBackend = true) => {
    if (!isLanguageSupported(languageCode)) {
      throw new Error(`Unsupported language: ${languageCode}`)
    }
    
    if (languageCode === locale.value) {
      return true // Already set
    }
    
    try {
      loading.value = true
      error.value = null
      
      // Update Vue I18n locale
      locale.value = languageCode
      
      // Store in localStorage
      localStorage.setItem('user-language', languageCode)
      
      // Update user preference in backend if authenticated and requested
      if (updateBackend) {
        const token = localStorage.getItem('auth-token')
        if (token) {
          const response = await fetch('/api/user/language', {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: languageCode })
          })
          
          if (!response.ok) {
            throw new Error('Failed to update language preference on server')
          }
        }
      }
      
      return true
    } catch (err) {
      error.value = err.message
      // Revert locale on error
      const previousLanguage = getStoredLanguage() || getBrowserLanguage()
      locale.value = previousLanguage
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Format language name for display
  const formatLanguageName = (languageCode, displayLanguage = null) => {
    const language = availableLanguages.find(lang => lang.code === languageCode)
    if (!language) return languageCode
    
    // If displayLanguage is specified, try to get localized name
    if (displayLanguage && displayLanguage !== languageCode) {
      // For now, just return the native name
      // In the future, this could be enhanced with localized language names
      return language.name
    }
    
    return language.name
  }
  
  // Get language direction (for RTL support in the future)
  const getLanguageDirection = (languageCode = null) => {
    const code = languageCode || locale.value
    // Currently all supported languages are LTR
    // This can be extended for RTL languages like Arabic, Hebrew
    const rtlLanguages = ['ar', 'he', 'fa']
    return rtlLanguages.includes(code) ? 'rtl' : 'ltr'
  }
  
  return {
    // State
    loading,
    error,
    
    // Computed
    currentLanguage,
    availableLanguages,
    
    // Methods
    changeLanguage,
    initializeLanguage,
    isLanguageSupported,
    formatLanguageName,
    getLanguageDirection,
    getBrowserLanguage,
    getStoredLanguage
  }
}
