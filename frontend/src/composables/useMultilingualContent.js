/**
 * Composable for multilingual content support
 * Handles wine information, error messages, and dynamic content translation
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

export function useMultilingualContent() {
  const { t, locale } = useI18n()
  
  // Format wine information with localized content
  const formatWineInfo = (wine) => {
    if (!wine) return null
    
    return {
      ...wine,
      // Use localized name if available, fallback to original
      displayName: getLocalizedWineName(wine),
      displayRegion: getLocalizedWineRegion(wine),
      displayType: getLocalizedWineType(wine.type),
      displayTastingNotes: getLocalizedTastingNotes(wine)
    }
  }
  
  // Get localized wine name
  const getLocalizedWineName = (wine) => {
    if (!wine) return ''
    
    // Check if wine has localized names
    if (wine.name_translations && wine.name_translations[locale.value]) {
      return wine.name_translations[locale.value]
    }
    
    // Fallback to original name
    return wine.name || ''
  }
  
  // Get localized wine region
  const getLocalizedWineRegion = (wine) => {
    if (!wine) return ''
    
    // Check if wine has localized region names
    if (wine.region_translations && wine.region_translations[locale.value]) {
      return wine.region_translations[locale.value]
    }
    
    // Fallback to original region
    return wine.region || ''
  }
  
  // Get localized wine type
  const getLocalizedWineType = (wineType) => {
    if (!wineType) return ''
    
    // Use translation key for wine types
    const typeKey = `wine.type.${wineType.toLowerCase()}`
    const translated = t(typeKey)
    
    // If translation key not found, return original
    return translated !== typeKey ? translated : wineType
  }
  
  // Get localized tasting notes
  const getLocalizedTastingNotes = (wine) => {
    if (!wine) return ''
    
    // Check if wine has localized tasting notes
    if (wine.tasting_notes_translations && wine.tasting_notes_translations[locale.value]) {
      return wine.tasting_notes_translations[locale.value]
    }
    
    // Fallback to original tasting notes
    return wine.tasting_notes || ''
  }
  
  // Format error messages with context
  const formatErrorMessage = (error, context = {}) => {
    if (!error) return ''
    
    // If error is already a translation key
    if (typeof error === 'string' && error.includes('.')) {
      return t(error, context)
    }
    
    // Map common error types to translation keys
    const errorMappings = {
      'network_error': 'common.error_network',
      'timeout': 'common.error_timeout',
      'unauthorized': 'common.error_unauthorized',
      'forbidden': 'common.error_forbidden',
      'not_found': 'common.error_not_found',
      'server_error': 'common.error_server',
      'validation_error': 'common.error_validation'
    }
    
    const errorKey = errorMappings[error] || 'common.error'
    return t(errorKey, context)
  }
  
  // Format date/time according to locale
  const formatDateTime = (dateTime, options = {}) => {
    if (!dateTime) return ''
    
    const date = new Date(dateTime)
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
    
    return new Intl.DateTimeFormat(locale.value, { ...defaultOptions, ...options }).format(date)
  }
  
  // Format numbers according to locale
  const formatNumber = (number, options = {}) => {
    if (number === null || number === undefined) return ''
    
    return new Intl.NumberFormat(locale.value, options).format(number)
  }
  
  // Format currency according to locale
  const formatCurrency = (amount, currency = 'USD') => {
    if (amount === null || amount === undefined) return ''
    
    return new Intl.NumberFormat(locale.value, {
      style: 'currency',
      currency: currency
    }).format(amount)
  }
  
  // Format percentage according to locale
  const formatPercentage = (value, decimals = 1) => {
    if (value === null || value === undefined) return ''
    
    return new Intl.NumberFormat(locale.value, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value / 100)
  }
  
  // Get localized placeholder text
  const getLocalizedPlaceholder = (key, fallback = '') => {
    const translated = t(key)
    return translated !== key ? translated : fallback
  }
  
  // Format wine search results with localized content
  const formatWineSearchResults = (wines) => {
    if (!Array.isArray(wines)) return []
    
    return wines.map(wine => formatWineInfo(wine))
  }
  
  // Get localized validation messages
  const getValidationMessage = (field, rule, value = null) => {
    const key = `validation.${rule}`
    const context = { field: t(`fields.${field}`), value }
    
    return t(key, context)
  }
  
  // Format user-friendly file sizes
  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B'
    
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    const size = bytes / Math.pow(1024, i)
    
    return `${formatNumber(size, { maximumFractionDigits: 1 })} ${sizes[i]}`
  }
  
  // Get relative time formatting
  const formatRelativeTime = (dateTime) => {
    if (!dateTime) return ''
    
    const date = new Date(dateTime)
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    // Use Intl.RelativeTimeFormat for proper localization
    const rtf = new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' })
    
    if (diffInSeconds < 60) {
      return rtf.format(-diffInSeconds, 'second')
    } else if (diffInSeconds < 3600) {
      return rtf.format(-Math.floor(diffInSeconds / 60), 'minute')
    } else if (diffInSeconds < 86400) {
      return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour')
    } else if (diffInSeconds < 2592000) {
      return rtf.format(-Math.floor(diffInSeconds / 86400), 'day')
    } else if (diffInSeconds < 31536000) {
      return rtf.format(-Math.floor(diffInSeconds / 2592000), 'month')
    } else {
      return rtf.format(-Math.floor(diffInSeconds / 31536000), 'year')
    }
  }
  
  // Current locale info
  const currentLocale = computed(() => locale.value)
  
  return {
    // Wine-specific formatting
    formatWineInfo,
    getLocalizedWineName,
    getLocalizedWineRegion,
    getLocalizedWineType,
    getLocalizedTastingNotes,
    formatWineSearchResults,
    
    // Error and message formatting
    formatErrorMessage,
    getValidationMessage,
    getLocalizedPlaceholder,
    
    // Date and number formatting
    formatDateTime,
    formatNumber,
    formatCurrency,
    formatPercentage,
    formatFileSize,
    formatRelativeTime,
    
    // Current locale
    currentLocale
  }
}