/**
 * Authentication store using Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth-token'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const userLanguage = computed(() => user.value?.main_language || 'ja')

  // Actions
  async function login(userData, authToken) {
    try {
      loading.value = true
      error.value = null

      user.value = userData
      token.value = authToken

      // Store token in localStorage
      localStorage.setItem('auth-token', authToken)

      // Update language preference
      if (userData.main_language) {
        localStorage.setItem('user-language', userData.main_language)
      }

      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      loading.value = true

      // Call logout API if needed
      if (token.value) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json'
          }
        })
      }

      // Clear state
      user.value = null
      token.value = null

      // Clear localStorage
      localStorage.removeItem('auth-token')

      return true
    } catch (err) {
      console.error('Logout error:', err)
      // Clear state even if API call fails
      user.value = null
      token.value = null
      localStorage.removeItem('auth-token')
      return true
    } finally {
      loading.value = false
    }
  }

  async function refreshUser() {
    if (!token.value) return false

    try {
      loading.value = true
      error.value = null

      const response = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to refresh user data')
      }

      const userData = await response.json()
      user.value = userData

      return true
    } catch (err) {
      error.value = err.message
      // Clear invalid token
      await logout()
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateUserLanguage(language) {
    if (!user.value) return false

    try {
      loading.value = true
      error.value = null

      const response = await fetch('/api/user/language', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ language })
      })

      if (!response.ok) {
        throw new Error('Failed to update language')
      }

      // Update local state
      user.value.main_language = language
      localStorage.setItem('user-language', language)

      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function linkOAuthProvider(provider, authData) {
    if (!user.value) return false

    try {
      loading.value = true
      error.value = null

      const response = await fetch('/api/auth/link-provider', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider,
          authData
        })
      })

      if (!response.ok) {
        throw new Error('Failed to link OAuth provider')
      }

      // Refresh user data to get updated provider list
      await refreshUser()

      return true
    } catch (err) {
      error.value = err.message
      return false
    } finally {
      loading.value = false
    }
  }

  // Initialize store
  async function initialize() {
    if (token.value) {
      await refreshUser()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    userLanguage,
    
    // Actions
    login,
    logout,
    refreshUser,
    updateUserLanguage,
    linkOAuthProvider,
    initialize
  }
})