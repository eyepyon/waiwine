/**
 * Vue I18n internationalization configuration
 */
import { createI18n } from 'vue-i18n'
import ja from './locales/ja.json'
import en from './locales/en.json'
import ko from './locales/ko.json'
import zh from './locales/zh.json'
import es from './locales/es.json'
import fr from './locales/fr.json'
import de from './locales/de.json'

const messages = {
  ja,
  en,
  ko,
  zh,
  es,
  fr,
  de
}

// Get user's preferred language from localStorage or browser
function getDefaultLocale() {
  const stored = localStorage.getItem('user-language')
  if (stored && messages[stored]) {
    return stored
  }
  
  const browserLang = navigator.language.split('-')[0]
  return messages[browserLang] ? browserLang : 'ja'
}

const i18n = createI18n({
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages,
  legacy: false,
  globalInjection: true
})

export default i18n

export const availableLanguages = [
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
]