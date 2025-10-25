<template>
  <div class="translation-settings">
    <div class="settings-header">
      <h2>{{ $t('translation.settings_title') }}</h2>
      <p class="settings-description">{{ $t('translation.settings_description') }}</p>
    </div>

    <div class="settings-form">
      <!-- Translation Features -->
      <div class="settings-section">
        <h3>{{ $t('translation.features') }}</h3>
        
        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.enable_text') }}</label>
            <p class="setting-description">{{ $t('translation.text_description') }}</p>
          </div>
          <div class="setting-control">
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="settings.textTranslationEnabled"
                @change="saveSettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.enable_voice') }}</label>
            <p class="setting-description">{{ $t('translation.voice_description') }}</p>
          </div>
          <div class="setting-control">
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="settings.voiceTranslationEnabled"
                @change="saveSettings"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Audio Settings -->
      <div v-if="settings.voiceTranslationEnabled" class="settings-section">
        <h3>{{ $t('translation.audio_settings') }}</h3>
        
        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.original_volume') }}</label>
            <p class="setting-description">{{ $t('translation.original_volume_description') }}</p>
          </div>
          <div class="setting-control">
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                v-model="settings.originalVoiceVolume"
                @input="saveSettings"
                class="volume-slider"
              />
              <span class="volume-display">{{ Math.round(settings.originalVoiceVolume * 100) }}%</span>
            </div>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.translated_volume') }}</label>
            <p class="setting-description">{{ $t('translation.translated_volume_description') }}</p>
          </div>
          <div class="setting-control">
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                v-model="settings.translatedVoiceVolume"
                @input="saveSettings"
                class="volume-slider"
              />
              <span class="volume-display">{{ Math.round(settings.translatedVoiceVolume * 100) }}%</span>
            </div>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.voice_speed') }}</label>
            <p class="setting-description">{{ $t('translation.voice_speed_description') }}</p>
          </div>
          <div class="setting-control">
            <div class="speed-control">
              <input 
                type="range" 
                min="0.5" 
                max="2.0" 
                step="0.1"
                v-model="settings.voiceSpeed"
                @input="saveSettings"
                class="speed-slider"
              />
              <span class="speed-display">{{ settings.voiceSpeed }}x</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Voice Selection -->
      <div v-if="settings.voiceTranslationEnabled" class="settings-section">
        <h3>{{ $t('translation.voice_selection') }}</h3>
        
        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.preferred_voice') }}</label>
            <p class="setting-description">{{ $t('translation.voice_selection_description') }}</p>
          </div>
          <div class="setting-control">
            <select 
              v-model="settings.preferredVoiceId" 
              @change="saveSettings"
              class="voice-select"
            >
              <option value="">{{ $t('translation.default_voice') }}</option>
              <option 
                v-for="voice in availableVoices" 
                :key="voice.id" 
                :value="voice.id"
              >
                {{ voice.name }} ({{ voice.gender }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="settings.preferredVoiceId" class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.voice_preview') }}</label>
            <p class="setting-description">{{ $t('translation.voice_preview_description') }}</p>
          </div>
          <div class="setting-control">
            <button 
              @click="playVoicePreview" 
              :disabled="isPlayingPreview"
              class="preview-button"
            >
              <i class="fas fa-play" v-if="!isPlayingPreview"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ $t('translation.play_preview') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Subtitle Settings -->
      <div v-if="settings.textTranslationEnabled" class="settings-section">
        <h3>{{ $t('translation.subtitle_settings') }}</h3>
        
        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.subtitle_position') }}</label>
            <p class="setting-description">{{ $t('translation.subtitle_position_description') }}</p>
          </div>
          <div class="setting-control">
            <select 
              v-model="settings.subtitlePosition" 
              @change="saveSettings"
              class="position-select"
            >
              <option value="top">{{ $t('translation.position_top') }}</option>
              <option value="bottom">{{ $t('translation.position_bottom') }}</option>
              <option value="overlay">{{ $t('translation.position_overlay') }}</option>
            </select>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.subtitle_font_size') }}</label>
            <p class="setting-description">{{ $t('translation.font_size_description') }}</p>
          </div>
          <div class="setting-control">
            <div class="font-size-control">
              <input 
                type="range" 
                min="12" 
                max="24" 
                step="1"
                v-model="settings.subtitleFontSize"
                @input="saveSettings"
                class="font-size-slider"
              />
              <span class="font-size-display">{{ settings.subtitleFontSize }}px</span>
            </div>
          </div>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <label>{{ $t('translation.subtitle_opacity') }}</label>
            <p class="setting-description">{{ $t('translation.opacity_description') }}</p>
          </div>
          <div class="setting-control">
            <div class="opacity-control">
              <input 
                type="range" 
                min="0.3" 
                max="1.0" 
                step="0.1"
                v-model="settings.subtitleBackgroundOpacity"
                @input="saveSettings"
                class="opacity-slider"
              />
              <span class="opacity-display">{{ Math.round(settings.subtitleBackgroundOpacity * 100) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Status -->
      <div v-if="saveStatus" class="save-status" :class="saveStatus.type">
        <i class="fas fa-check-circle" v-if="saveStatus.type === 'success'"></i>
        <i class="fas fa-exclamation-triangle" v-else></i>
        {{ saveStatus.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'TranslationSettings',
  setup() {
    const { t } = useI18n()
    const authStore = useAuthStore()

    // Reactive data
    const availableVoices = ref([])
    const isPlayingPreview = ref(false)
    const saveStatus = ref(null)
    const audioContext = ref(null)

    const settings = reactive({
      textTranslationEnabled: true,
      voiceTranslationEnabled: false,
      originalVoiceVolume: 0.3,
      translatedVoiceVolume: 0.8,
      preferredVoiceId: '',
      voiceSpeed: 1.0,
      subtitlePosition: 'bottom',
      subtitleFontSize: 16,
      subtitleBackgroundOpacity: 0.7
    })

    // Methods
    const loadSettings = async () => {
      try {
        const response = await fetch('/api/translation/settings', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          Object.assign(settings, data)
        }
      } catch (error) {
        console.error('Failed to load translation settings:', error)
        showSaveStatus('error', t('translation.load_error'))
      }
    }

    const loadAvailableVoices = async () => {
      try {
        const userLanguage = authStore.user?.main_language || 'ja'
        const response = await fetch(`/api/translation/voices/${userLanguage}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          availableVoices.value = await response.json()
        }
      } catch (error) {
        console.error('Failed to load available voices:', error)
      }
    }

    const saveSettings = async () => {
      try {
        const response = await fetch('/api/translation/settings', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(settings)
        })

        if (response.ok) {
          showSaveStatus('success', t('translation.save_success'))
        } else {
          throw new Error('Failed to save settings')
        }
      } catch (error) {
        console.error('Failed to save translation settings:', error)
        showSaveStatus('error', t('translation.save_error'))
      }
    }

    const playVoicePreview = async () => {
      if (!settings.preferredVoiceId || isPlayingPreview.value) {
        return
      }

      try {
        isPlayingPreview.value = true
        
        const sampleText = t('translation.sample_text')
        const response = await fetch('/api/translation/synthesize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            text: sampleText,
            voice_id: settings.preferredVoiceId,
            speed: settings.voiceSpeed
          })
        })

        if (response.ok) {
          const result = await response.json()
          await playAudioFromBase64(result.audio_data)
        } else {
          throw new Error('Failed to generate voice preview')
        }
      } catch (error) {
        console.error('Failed to play voice preview:', error)
        showSaveStatus('error', t('translation.preview_error'))
      } finally {
        isPlayingPreview.value = false
      }
    }

    const playAudioFromBase64 = async (base64Audio) => {
      try {
        if (!audioContext.value) {
          audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
        }

        // Decode base64 audio data
        const audioData = atob(base64Audio)
        const audioBuffer = new ArrayBuffer(audioData.length)
        const audioArray = new Uint8Array(audioBuffer)
        
        for (let i = 0; i < audioData.length; i++) {
          audioArray[i] = audioData.charCodeAt(i)
        }

        // Decode and play audio
        const decodedAudio = await audioContext.value.decodeAudioData(audioBuffer)
        const source = audioContext.value.createBufferSource()
        
        source.buffer = decodedAudio
        source.connect(audioContext.value.destination)
        source.start()

        return new Promise((resolve) => {
          source.onended = resolve
        })
      } catch (error) {
        console.error('Failed to play audio:', error)
        throw error
      }
    }

    const showSaveStatus = (type, message) => {
      saveStatus.value = { type, message }
      setTimeout(() => {
        saveStatus.value = null
      }, 3000)
    }

    // Lifecycle
    onMounted(async () => {
      await loadSettings()
      await loadAvailableVoices()
    })

    return {
      settings,
      availableVoices,
      isPlayingPreview,
      saveStatus,
      saveSettings,
      playVoicePreview
    }
  }
}
</script>

<style scoped>
.translation-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-header {
  margin-bottom: 30px;
}

.settings-header h2 {
  color: #333;
  margin-bottom: 8px;
}

.settings-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.settings-form {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.settings-section {
  padding: 24px;
  border-bottom: 1px solid #eee;
}

.settings-section:last-child {
  border-bottom: none;
}

.settings-section h3 {
  color: #333;
  margin: 0 0 20px 0;
  font-size: 18px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 20px;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-info {
  flex: 1;
}

.setting-info label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.setting-description {
  color: #666;
  font-size: 14px;
  margin: 0;
  line-height: 1.4;
}

.setting-control {
  flex-shrink: 0;
}

/* Toggle Switch */
.toggle-switch {
  display: inline-block;
  position: relative;
  cursor: pointer;
}

.toggle-switch input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  width: 50px;
  height: 26px;
  background: #ccc;
  border-radius: 13px;
  position: relative;
  transition: background 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.toggle-switch input[type="checkbox"]:checked + .toggle-slider {
  background: #4CAF50;
}

.toggle-switch input[type="checkbox"]:checked + .toggle-slider::before {
  transform: translateX(24px);
}

/* Volume, Speed, Font Size, Opacity Controls */
.volume-control,
.speed-control,
.font-size-control,
.opacity-control {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.volume-slider,
.speed-slider,
.font-size-slider,
.opacity-slider {
  flex: 1;
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb,
.speed-slider::-webkit-slider-thumb,
.font-size-slider::-webkit-slider-thumb,
.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
}

.volume-display,
.speed-display,
.font-size-display,
.opacity-display {
  min-width: 45px;
  text-align: right;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* Select Inputs */
.voice-select,
.position-select {
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.voice-select:focus,
.position-select:focus {
  outline: none;
  border-color: #4CAF50;
}

/* Preview Button */
.preview-button {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.preview-button:hover:not(:disabled) {
  background: #45a049;
}

.preview-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Save Status */
.save-status {
  margin: 20px 24px;
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.save-status.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.save-status.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Responsive Design */
@media (max-width: 768px) {
  .translation-settings {
    padding: 16px;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .volume-control,
  .speed-control,
  .font-size-control,
  .opacity-control {
    min-width: auto;
  }
  
  .voice-select,
  .position-select {
    min-width: auto;
    width: 100%;
  }
  
  .preview-button {
    width: 100%;
  }
}
</style>