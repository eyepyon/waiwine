<template>
  <div class="user-settings">
    <div class="settings-container">
      <div class="settings-header">
        <h1>{{ $t('settings.title') }}</h1>
        <p>{{ $t('settings.subtitle') }}</p>
      </div>
      
      <!-- Profile Settings -->
      <div class="settings-section">
        <h2>{{ $t('settings.profile') }}</h2>
        
        <div class="profile-info">
          <div class="profile-avatar">
            <img 
              v-if="userProfile.profile_image_url" 
              :src="userProfile.profile_image_url" 
              :alt="userProfile.name"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              {{ userProfile.name?.charAt(0)?.toUpperCase() }}
            </div>
          </div>
          
          <div class="profile-details">
            <h3>{{ userProfile.name }}</h3>
            <p class="email">{{ userProfile.email }}</p>
            <p class="member-since">
              {{ $t('settings.member_since') }}: {{ formatDate(userProfile.created_at) }}
            </p>
          </div>
        </div>
        
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label for="name">{{ $t('settings.display_name') }}</label>
            <input
              id="name"
              v-model="profileForm.name"
              type="text"
              :placeholder="$t('settings.display_name_placeholder')"
              required
            />
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              :disabled="profileLoading || !profileChanged"
              class="save-btn"
            >
              {{ profileLoading ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
      
      <!-- Language Settings -->
      <div class="settings-section">
        <h2>{{ $t('settings.language') }}</h2>
        
        <div class="language-selector">
          <label for="language">{{ $t('settings.main_language') }}</label>
          <select 
            id="language" 
            v-model="selectedLanguage" 
            @change="updateLanguage"
            :disabled="languageLoading"
          >
            <option 
              v-for="lang in availableLanguages" 
              :key="lang.code" 
              :value="lang.code"
            >
              {{ lang.name }} ({{ lang.english_name }})
            </option>
          </select>
        </div>
      </div>
      
      <!-- OAuth Providers -->
      <div class="settings-section">
        <h2>{{ $t('settings.connected_accounts') }}</h2>
        
        <div class="oauth-providers">
          <div 
            v-for="provider in allProviders" 
            :key="provider.name"
            class="provider-item"
          >
            <div class="provider-info">
              <span class="provider-icon">{{ provider.icon }}</span>
              <div class="provider-details">
                <h4>{{ provider.displayName }}</h4>
                <p v-if="provider.connected" class="connected-email">
                  {{ provider.email || $t('settings.connected') }}
                </p>
                <p v-else class="not-connected">
                  {{ $t('settings.not_connected') }}
                </p>
              </div>
            </div>
            
            <div class="provider-actions">
              <button
                v-if="provider.connected"
                @click="unlinkProvider(provider.name)"
                :disabled="!provider.canUnlink || unlinkingProvider === provider.name"
                class="unlink-btn"
              >
                {{ unlinkingProvider === provider.name ? $t('common.loading') : $t('settings.unlink') }}
              </button>
              <button
                v-else
                @click="linkProvider(provider.name)"
                :disabled="linkingProvider === provider.name"
                class="link-btn"
              >
                {{ linkingProvider === provider.name ? $t('common.loading') : $t('settings.link') }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Translation Settings -->
      <div class="settings-section">
        <h2>{{ $t('translation.settings_title') }}</h2>
        <p>{{ $t('translation.settings_description') }}</p>
        
        <div class="translation-preview">
          <div class="preview-item">
            <span class="preview-label">{{ $t('translation.enable_text') }}:</span>
            <span :class="['preview-status', { enabled: translationSettings.text_translation_enabled }]">
              {{ translationSettings.text_translation_enabled ? $t('common.enabled') : $t('common.disabled') }}
            </span>
          </div>
          
          <div class="preview-item">
            <span class="preview-label">{{ $t('translation.enable_voice') }}:</span>
            <span :class="['preview-status', { enabled: translationSettings.voice_translation_enabled }]">
              {{ translationSettings.voice_translation_enabled ? $t('common.enabled') : $t('common.disabled') }}
            </span>
          </div>
        </div>
        
        <div class="form-actions">
          <router-link to="/settings/translation" class="settings-link-btn">
            {{ $t('translation.advanced_settings') }}
          </router-link>
        </div>
      </div>
      
      <!-- Account Actions -->
      <div class="settings-section danger-section">
        <h2>{{ $t('settings.account_actions') }}</h2>
        
        <div class="danger-actions">
          <button @click="showDeleteConfirmation = true" class="delete-btn">
            {{ $t('settings.delete_account') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Account Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-overlay" @click="showDeleteConfirmation = false">
      <div class="modal-content" @click.stop>
        <h3>{{ $t('settings.confirm_delete') }}</h3>
        <p>{{ $t('settings.delete_warning') }}</p>
        
        <div class="modal-actions">
          <button @click="showDeleteConfirmation = false" class="cancel-btn">
            {{ $t('common.cancel') }}
          </button>
          <button @click="deleteAccount" :disabled="deletingAccount" class="confirm-delete-btn">
            {{ deletingAccount ? $t('common.deleting') : $t('settings.confirm_delete_btn') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { availableLanguages } from '@/i18n'

export default {
  name: 'UserSettings',
  
  data() {
    return {
      userProfile: {},
      profileForm: {
        name: ''
      },
      selectedLanguage: '',
      translationSettings: {
        text_translation_enabled: true,
        voice_translation_enabled: false,
        original_voice_volume: 0.3,
        translated_voice_volume: 0.8
      },
      
      availableLanguages,
      allProviders: [
        {
          name: 'google',
          displayName: 'Google',
          icon: '🔍',
          connected: false,
          email: null,
          canUnlink: true
        },
        {
          name: 'twitter',
          displayName: 'X (Twitter)',
          icon: '🐦',
          connected: false,
          email: null,
          canUnlink: true
        },
        {
          name: 'line',
          displayName: 'LINE',
          icon: '💬',
          connected: false,
          email: null,
          canUnlink: true
        }
      ],
      
      // Loading states
      profileLoading: false,
      languageLoading: false,
      translationLoading: false,
      linkingProvider: null,
      unlinkingProvider: null,
      deletingAccount: false,
      
      // UI state
      showDeleteConfirmation: false,
      message: '',
      messageType: 'success'
    }
  },
  
  computed: {
    profileChanged() {
      return this.profileForm.name !== this.userProfile.name
    }
  },
  
  async mounted() {
    await this.loadUserData()
  },
  
  methods: {
    async loadUserData() {
      try {
        const authStore = useAuthStore()
        
        // Load user profile
        const profileResponse = await fetch('/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (profileResponse.ok) {
          this.userProfile = await profileResponse.json()
          this.profileForm.name = this.userProfile.name
          this.selectedLanguage = this.userProfile.main_language
          
          // Update connected providers
          this.updateConnectedProviders(this.userProfile.oauth_providers)
        }
        
        // Load translation settings
        const translationResponse = await fetch('/api/user/translation-settings', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (translationResponse.ok) {
          this.translationSettings = await translationResponse.json()
        }
        
      } catch (error) {
        console.error('Failed to load user data:', error)
        this.showMessage('Failed to load user data', 'error')
      }
    },
    
    updateConnectedProviders(oauthProviders) {
      this.allProviders.forEach(provider => {
        const connected = oauthProviders.find(p => p.provider === provider.name)
        provider.connected = !!connected
        provider.email = connected?.provider_email || null
      })
    },
    
    async updateProfile() {
      this.profileLoading = true
      
      try {
        const authStore = useAuthStore()
        
        const response = await fetch('/api/user/profile', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.profileForm.name
          })
        })
        
        if (response.ok) {
          this.userProfile.name = this.profileForm.name
          this.showMessage('Profile updated successfully', 'success')
        } else {
          throw new Error('Failed to update profile')
        }
        
      } catch (error) {
        console.error('Profile update error:', error)
        this.showMessage('Failed to update profile', 'error')
      } finally {
        this.profileLoading = false
      }
    },
    
    async updateLanguage() {
      this.languageLoading = true
      
      try {
        const authStore = useAuthStore()
        
        const response = await fetch('/api/user/language', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            language: this.selectedLanguage
          })
        })
        
        if (response.ok) {
          // Update app language
          this.$i18n.locale = this.selectedLanguage
          localStorage.setItem('user-language', this.selectedLanguage)
          
          // Update auth store
          await authStore.updateUserLanguage(this.selectedLanguage)
          
          this.showMessage('Language updated successfully', 'success')
        } else {
          throw new Error('Failed to update language')
        }
        
      } catch (error) {
        console.error('Language update error:', error)
        this.showMessage('Failed to update language', 'error')
        // Revert selection
        this.selectedLanguage = this.userProfile.main_language
      } finally {
        this.languageLoading = false
      }
    },
    
    async updateTranslationSettings() {
      this.translationLoading = true
      
      try {
        const authStore = useAuthStore()
        
        const response = await fetch('/api/user/translation-settings', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.translationSettings)
        })
        
        if (response.ok) {
          this.showMessage('Translation settings updated successfully', 'success')
        } else {
          throw new Error('Failed to update translation settings')
        }
        
      } catch (error) {
        console.error('Translation settings update error:', error)
        this.showMessage('Failed to update translation settings', 'error')
      } finally {
        this.translationLoading = false
      }
    },
    
    async linkProvider(providerName) {
      this.linkingProvider = providerName
      
      try {
        // Get authorization URL
        const response = await fetch('/api/auth/authorize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            provider: providerName,
            redirect_url: window.location.href
          })
        })
        
        if (!response.ok) {
          throw new Error('Failed to get authorization URL')
        }
        
        const data = await response.json()
        
        // Open OAuth popup
        const popup = window.open(
          data.authorization_url,
          `${providerName}_oauth`,
          'width=500,height=600,scrollbars=yes,resizable=yes'
        )
        
        // Handle OAuth result
        const result = await this.handleOAuthPopup(popup)
        
        if (result.success) {
          await this.loadUserData() // Refresh data
          this.showMessage(`Successfully linked ${providerName} account`, 'success')
        }
        
      } catch (error) {
        console.error('Link provider error:', error)
        this.showMessage(`Failed to link ${providerName} account`, 'error')
      } finally {
        this.linkingProvider = null
      }
    },
    
    async unlinkProvider(providerName) {
      this.unlinkingProvider = providerName
      
      try {
        const authStore = useAuthStore()
        
        const response = await fetch('/api/auth/unlink-provider', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            provider: providerName
          })
        })
        
        if (response.ok) {
          await this.loadUserData() // Refresh data
          this.showMessage(`Successfully unlinked ${providerName} account`, 'success')
        } else {
          throw new Error('Failed to unlink provider')
        }
        
      } catch (error) {
        console.error('Unlink provider error:', error)
        this.showMessage(`Failed to unlink ${providerName} account`, 'error')
      } finally {
        this.unlinkingProvider = null
      }
    },
    
    async deleteAccount() {
      this.deletingAccount = true
      
      try {
        const authStore = useAuthStore()
        
        const response = await fetch('/api/user/account', {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          // Logout and redirect
          await authStore.logout()
          this.$router.push('/')
        } else {
          throw new Error('Failed to delete account')
        }
        
      } catch (error) {
        console.error('Delete account error:', error)
        this.showMessage('Failed to delete account', 'error')
      } finally {
        this.deletingAccount = false
        this.showDeleteConfirmation = false
      }
    },
    
    handleOAuthPopup(popup) {
      return new Promise((resolve, reject) => {
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed)
            reject(new Error('OAuth popup was closed'))
          }
        }, 1000)
        
        const messageHandler = (event) => {
          if (event.origin !== window.location.origin) return
          
          if (event.data.type === 'oauth_success') {
            clearInterval(checkClosed)
            popup.close()
            window.removeEventListener('message', messageHandler)
            resolve({ success: true, result: event.data.result })
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
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString(this.$i18n.locale)
    },
    
    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      
      setTimeout(() => {
        this.message = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.user-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.settings-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.settings-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.settings-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.settings-header p {
  margin: 0;
  opacity: 0.9;
}

.settings-section {
  padding: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.settings-section:last-child {
  border-bottom: none;
}

.settings-section h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.25rem;
}

.profile-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 2rem;
  font-weight: bold;
  color: #666;
}

.profile-details h3 {
  margin: 0 0 0.25rem 0;
  color: #333;
}

.email {
  color: #666;
  margin: 0 0 0.25rem 0;
}

.member-since {
  color: #999;
  font-size: 0.9rem;
  margin: 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.volume-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
}

.volume-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
  border: none;
}

.translation-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-weight: 500;
  color: #333;
}

.preview-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  background: #dc3545;
  color: white;
}

.preview-status.enabled {
  background: #28a745;
}

.settings-link-btn {
  display: inline-block;
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.settings-link-btn:hover {
  background: #5a6268;
  color: white;
  text-decoration: none;
}

.oauth-providers {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.provider-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: #f9f9f9;
}

.provider-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.provider-icon {
  font-size: 1.5rem;
}

.provider-details h4 {
  margin: 0 0 0.25rem 0;
  color: #333;
}

.connected-email {
  color: #28a745;
  margin: 0;
  font-size: 0.9rem;
}

.not-connected {
  color: #666;
  margin: 0;
  font-size: 0.9rem;
}

.form-actions,
.provider-actions {
  display: flex;
  gap: 0.5rem;
}

.save-btn,
.link-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-btn:hover:not(:disabled),
.link-btn:hover:not(:disabled) {
  background: #0056b3;
}

.unlink-btn {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.unlink-btn:hover:not(:disabled) {
  background: #c82333;
}

.save-btn:disabled,
.link-btn:disabled,
.unlink-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-section {
  background: #fff5f5;
}

.delete-btn {
  padding: 12px 24px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.delete-btn:hover {
  background: #c82333;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.modal-content h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.modal-content p {
  margin: 0 0 2rem 0;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.confirm-delete-btn {
  padding: 10px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1001;
}

.message.success {
  background: #28a745;
}

.message.error {
  background: #dc3545;
}

@media (max-width: 768px) {
  .user-settings {
    padding: 1rem;
  }
  
  .settings-section {
    padding: 1.5rem;
  }
  
  .provider-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .provider-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>