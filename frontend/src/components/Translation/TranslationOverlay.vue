<template>
  <div class="translation-overlay">
    <!-- Subtitle Display -->
    <div 
      v-if="translationSettings.textTranslationEnabled && currentTranslation"
      :class="['subtitle-container', `position-${translationSettings.subtitlePosition}`]"
      :style="subtitleStyles"
    >
      <div class="subtitle-content">
        <div class="original-text">
          <span class="speaker-name">{{ getSpeakerName(currentTranslation.speakerId) }}:</span>
          {{ currentTranslation.originalText }}
        </div>
        <div class="translated-text">
          {{ currentTranslation.translatedText }}
        </div>
      </div>
    </div>

    <!-- Translation Settings Panel -->
    <div v-if="showSettings" class="translation-settings-panel">
      <div class="settings-header">
        <h3>{{ $t('translation.settings') }}</h3>
        <button @click="showSettings = false" class="close-btn">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="settings-content">
        <!-- Text Translation Toggle -->
        <div class="setting-group">
          <label class="toggle-label">
            <input 
              type="checkbox" 
              v-model="translationSettings.textTranslationEnabled"
              @change="updateSettings"
            />
            <span class="toggle-slider"></span>
            {{ $t('translation.enable_text') }}
          </label>
        </div>

        <!-- Voice Translation Toggle -->
        <div class="setting-group">
          <label class="toggle-label">
            <input 
              type="checkbox" 
              v-model="translationSettings.voiceTranslationEnabled"
              @change="updateSettings"
            />
            <span class="toggle-slider"></span>
            {{ $t('translation.enable_voice') }}
          </label>
        </div>

        <!-- Volume Controls -->
        <div v-if="translationSettings.voiceTranslationEnabled" class="setting-group">
          <div class="volume-control">
            <label>{{ $t('translation.original_volume') }}</label>
            <div class="volume-slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                v-model="translationSettings.originalVoiceVolume"
                @input="updateSettings"
                class="volume-slider"
              />
              <span class="volume-value">{{ Math.round(translationSettings.originalVoiceVolume * 100) }}%</span>
            </div>
          </div>

          <div class="volume-control">
            <label>{{ $t('translation.translated_volume') }}</label>
            <div class="volume-slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                v-model="translationSettings.translatedVoiceVolume"
                @input="updateSettings"
                class="volume-slider"
              />
              <span class="volume-value">{{ Math.round(translationSettings.translatedVoiceVolume * 100) }}%</span>
            </div>
          </div>
        </div>

        <!-- Voice Selection -->
        <div v-if="translationSettings.voiceTranslationEnabled" class="setting-group">
          <label>{{ $t('translation.voice_selection') }}</label>
          <select 
            v-model="translationSettings.preferredVoiceId" 
            @change="updateSettings"
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

          <!-- Voice Preview -->
          <button 
            @click="playVoicePreview" 
            :disabled="!translationSettings.preferredVoiceId || isPlayingPreview"
            class="preview-btn"
          >
            <i class="fas fa-play" v-if="!isPlayingPreview"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ $t('translation.preview_voice') }}
          </button>
        </div>

        <!-- Voice Speed -->
        <div v-if="translationSettings.voiceTranslationEnabled" class="setting-group">
          <label>{{ $t('translation.voice_speed') }}</label>
          <div class="speed-slider-container">
            <input 
              type="range" 
              min="0.5" 
              max="2.0" 
              step="0.1"
              v-model="translationSettings.voiceSpeed"
              @input="updateSettings"
              class="speed-slider"
            />
            <span class="speed-value">{{ translationSettings.voiceSpeed }}x</span>
          </div>
        </div>

        <!-- Subtitle Settings -->
        <div v-if="translationSettings.textTranslationEnabled" class="setting-group">
          <label>{{ $t('translation.subtitle_position') }}</label>
          <select 
            v-model="translationSettings.subtitlePosition" 
            @change="updateSettings"
            class="position-select"
          >
            <option value="top">{{ $t('translation.position_top') }}</option>
            <option value="bottom">{{ $t('translation.position_bottom') }}</option>
            <option value="overlay">{{ $t('translation.position_overlay') }}</option>
          </select>
        </div>

        <div v-if="translationSettings.textTranslationEnabled" class="setting-group">
          <label>{{ $t('translation.subtitle_font_size') }}</label>
          <div class="font-size-container">
            <input 
              type="range" 
              min="12" 
              max="24" 
              step="1"
              v-model="translationSettings.subtitleFontSize"
              @input="updateSettings"
              class="font-size-slider"
            />
            <span class="font-size-value">{{ translationSettings.subtitleFontSize }}px</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Toggle Button -->
    <button 
      @click="showSettings = !showSettings" 
      class="settings-toggle-btn"
      :class="{ active: showSettings }"
    >
      <i class="fas fa-cog"></i>
    </button>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'TranslationOverlay',
  props: {
    roomId: {
      type: String,
      required: true
    },
    participants: {
      type: Array,
      default: () => []
    }
  },
  emits: ['translation-ready', 'translation-error'],
  setup(props, { emit }) {
    const { t } = useI18n()
    const authStore = useAuthStore()

    // Reactive data
    const showSettings = ref(false)
    const currentTranslation = ref(null)
    const availableVoices = ref([])
    const isPlayingPreview = ref(false)
    const translationWebSocket = ref(null)
    const audioContext = ref(null)

    const translationSettings = reactive({
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

    // Computed properties
    const subtitleStyles = computed(() => ({
      fontSize: `${translationSettings.subtitleFontSize}px`,
      backgroundColor: `rgba(0, 0, 0, ${translationSettings.subtitleBackgroundOpacity})`
    }))

    // Methods
    const initializeTranslation = async () => {
      try {
        // Load user's translation settings
        await loadTranslationSettings()
        
        // Load available voices
        await loadAvailableVoices()
        
        // Initialize WebSocket connection
        await initializeWebSocket()
        
        emit('translation-ready')
      } catch (error) {
        console.error('Failed to initialize translation:', error)
        emit('translation-error', error)
      }
    }

    const loadTranslationSettings = async () => {
      try {
        const response = await fetch('/api/translation/settings', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const settings = await response.json()
          Object.assign(translationSettings, settings)
        }
      } catch (error) {
        console.error('Failed to load translation settings:', error)
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

    const initializeWebSocket = async () => {
      try {
        const wsUrl = `ws://localhost:8000/ws/translation/${authStore.user.id}/${props.roomId}?token=${authStore.token}`
        translationWebSocket.value = new WebSocket(wsUrl)

        translationWebSocket.value.onopen = () => {
          console.log('Translation WebSocket connected')
        }

        translationWebSocket.value.onmessage = (event) => {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        }

        translationWebSocket.value.onclose = () => {
          console.log('Translation WebSocket disconnected')
          // Attempt to reconnect after 3 seconds
          setTimeout(initializeWebSocket, 3000)
        }

        translationWebSocket.value.onerror = (error) => {
          console.error('Translation WebSocket error:', error)
        }

        // Initialize audio context for audio processing
        audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
        
      } catch (error) {
        console.error('Failed to initialize WebSocket:', error)
        throw error
      }
    }

    const handleWebSocketMessage = (data) => {
      switch (data.type) {
        case 'text_translation':
          displayTranslation(data)
          break
        case 'voice_translation':
          playTranslatedAudio(data)
          break
        case 'voices_list':
          availableVoices.value = data.voices
          break
        case 'settings_updated':
          console.log('Settings updated successfully')
          break
        case 'error':
          console.error('Translation error:', data.message)
          break
      }
    }

    const displayTranslation = (data) => {
      currentTranslation.value = {
        speakerId: data.speaker_id,
        originalText: data.original_text,
        translatedText: data.translated_text,
        sourceLanguage: data.source_language,
        targetLanguage: data.target_language
      }

      // Auto-hide after 5 seconds
      setTimeout(() => {
        if (currentTranslation.value && 
            currentTranslation.value.originalText === data.original_text) {
          currentTranslation.value = null
        }
      }, 5000)
    }

    const playTranslatedAudio = async (data) => {
      if (!translationSettings.voiceTranslationEnabled || !audioContext.value) {
        return
      }

      try {
        // Decode base64 audio data
        const audioData = atob(data.audio_data)
        const audioBuffer = new ArrayBuffer(audioData.length)
        const audioArray = new Uint8Array(audioBuffer)
        
        for (let i = 0; i < audioData.length; i++) {
          audioArray[i] = audioData.charCodeAt(i)
        }

        // Decode and play audio
        const decodedAudio = await audioContext.value.decodeAudioData(audioBuffer)
        const source = audioContext.value.createBufferSource()
        const gainNode = audioContext.value.createGain()

        source.buffer = decodedAudio
        gainNode.gain.value = translationSettings.translatedVoiceVolume

        source.connect(gainNode)
        gainNode.connect(audioContext.value.destination)

        source.start()
      } catch (error) {
        console.error('Failed to play translated audio:', error)
      }
    }

    const updateSettings = async () => {
      try {
        const response = await fetch('/api/translation/settings', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(translationSettings)
        })

        if (!response.ok) {
          throw new Error('Failed to update settings')
        }

        // Send settings update to WebSocket
        if (translationWebSocket.value?.readyState === WebSocket.OPEN) {
          translationWebSocket.value.send(JSON.stringify({
            type: 'update_settings',
            settings: translationSettings
          }))
        }
      } catch (error) {
        console.error('Failed to update translation settings:', error)
      }
    }

    const playVoicePreview = async () => {
      if (!translationSettings.preferredVoiceId || isPlayingPreview.value) {
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
            voice_id: translationSettings.preferredVoiceId,
            speed: translationSettings.voiceSpeed
          })
        })

        if (response.ok) {
          const result = await response.json()
          
          // Play the audio
          const audioData = atob(result.audio_data)
          const audioBuffer = new ArrayBuffer(audioData.length)
          const audioArray = new Uint8Array(audioBuffer)
          
          for (let i = 0; i < audioData.length; i++) {
            audioArray[i] = audioData.charCodeAt(i)
          }

          const decodedAudio = await audioContext.value.decodeAudioData(audioBuffer)
          const source = audioContext.value.createBufferSource()
          
          source.buffer = decodedAudio
          source.connect(audioContext.value.destination)
          source.start()

          source.onended = () => {
            isPlayingPreview.value = false
          }
        }
      } catch (error) {
        console.error('Failed to play voice preview:', error)
        isPlayingPreview.value = false
      }
    }

    const getSpeakerName = (speakerId) => {
      const participant = props.participants.find(p => p.id === speakerId)
      return participant?.name || t('translation.unknown_speaker')
    }

    const cleanup = () => {
      if (translationWebSocket.value) {
        translationWebSocket.value.close()
      }
      if (audioContext.value) {
        audioContext.value.close()
      }
    }

    const setupMobileOptimizations = () => {
      // Optimize for mobile performance
      if (window.innerWidth <= 768) {
        // Reduce translation frequency for mobile
        translationSettings.textTranslationEnabled = true
        translationSettings.voiceTranslationEnabled = false // Disable by default on mobile
      }
      
      // Handle orientation changes
      window.addEventListener('orientationchange', () => {
        setTimeout(() => {
          // Adjust subtitle position after orientation change
          if (currentTranslation.value) {
            // Force re-render of subtitles
            const temp = currentTranslation.value
            currentTranslation.value = null
            setTimeout(() => {
              currentTranslation.value = temp
            }, 50)
          }
        }, 100)
      })
      
      // Prevent settings panel from being accidentally closed on mobile
      if ('ontouchstart' in window) {
        const settingsPanel = document.querySelector('.translation-settings-panel')
        if (settingsPanel) {
          settingsPanel.addEventListener('touchmove', (e) => {
            e.stopPropagation()
          })
        }
      }
    }
    
    // Lifecycle
    onMounted(() => {
      setupMobileOptimizations()
      initializeTranslation()
    })

    onUnmounted(() => {
      cleanup()
    })

    return {
      showSettings,
      currentTranslation,
      availableVoices,
      isPlayingPreview,
      translationSettings,
      subtitleStyles,
      updateSettings,
      playVoicePreview,
      getSpeakerName
    }
  }
}
</script>

<style scoped>
.translation-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.translation-overlay > * {
  pointer-events: auto;
}

/* Subtitle Display */
.subtitle-container {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  max-width: 80%;
  z-index: 1000;
}

.subtitle-container.position-top {
  top: 20px;
}

.subtitle-container.position-bottom {
  bottom: 20px;
}

.subtitle-container.position-overlay {
  top: 50%;
  transform: translate(-50%, -50%);
}

.subtitle-content {
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  padding: 12px 16px;
  color: white;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.original-text {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.speaker-name {
  font-weight: bold;
  color: #4CAF50;
}

.translated-text {
  font-size: 16px;
  font-weight: 500;
}

/* Settings Panel */
.translation-settings-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  max-height: 80vh;
  overflow-y: auto;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.settings-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #666;
  cursor: pointer;
  padding: 4px;
}

.close-btn:hover {
  color: #333;
}

.settings-content {
  padding: 20px;
}

.setting-group {
  margin-bottom: 20px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

/* Toggle Switch */
.toggle-label {
  display: flex !important;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0 !important;
}

.toggle-label input[type="checkbox"] {
  display: none;
}

.toggle-slider {
  width: 44px;
  height: 24px;
  background: #ccc;
  border-radius: 12px;
  position: relative;
  margin-right: 12px;
  transition: background 0.3s;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider {
  background: #4CAF50;
}

.toggle-label input[type="checkbox"]:checked + .toggle-slider::before {
  transform: translateX(20px);
}

/* Volume Controls */
.volume-control {
  margin-bottom: 16px;
}

.volume-slider-container,
.speed-slider-container,
.font-size-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.volume-slider,
.speed-slider,
.font-size-slider {
  flex: 1;
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb,
.speed-slider::-webkit-slider-thumb,
.font-size-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
}

.volume-value,
.speed-value,
.font-size-value {
  min-width: 40px;
  text-align: right;
  font-size: 14px;
  color: #666;
}

/* Select Inputs */
.voice-select,
.position-select {
  width: 100%;
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
.preview-btn {
  margin-top: 8px;
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
}

.preview-btn:hover:not(:disabled) {
  background: #45a049;
}

.preview-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Settings Toggle Button */
.settings-toggle-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 48px;
  height: 48px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  z-index: 1000;
  transition: all 0.3s;
}

.settings-toggle-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.settings-toggle-btn.active {
  background: #4CAF50;
}

/* Mobile-responsive design */
@media (max-width: 768px) {
  .translation-settings-panel {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100vh;
    border-radius: 0;
    max-height: none;
    z-index: 2000;
    display: flex;
    flex-direction: column;
  }
  
  .settings-header {
    padding: 1rem;
    border-bottom: 2px solid #eee;
    flex-shrink: 0;
  }
  
  .settings-header h3 {
    font-size: 1.25rem;
  }
  
  .close-btn {
    font-size: 24px;
    padding: 8px;
    min-width: 44px;
    min-height: 44px;
  }
  
  .settings-content {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
  }
  
  .setting-group {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .setting-group:last-child {
    border-bottom: none;
    margin-bottom: 0;
  }
  
  .setting-group label {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }
  
  .toggle-label {
    padding: 0.5rem 0;
  }
  
  .toggle-slider {
    width: 52px;
    height: 28px;
    margin-right: 1rem;
  }
  
  .toggle-slider::before {
    width: 24px;
    height: 24px;
  }
  
  .toggle-label input[type="checkbox"]:checked + .toggle-slider::before {
    transform: translateX(24px);
  }
  
  .volume-control {
    margin-bottom: 1.25rem;
  }
  
  .volume-slider-container,
  .speed-slider-container,
  .font-size-container {
    gap: 1rem;
    margin-top: 0.5rem;
  }
  
  .volume-slider,
  .speed-slider,
  .font-size-slider {
    height: 8px;
  }
  
  .volume-slider::-webkit-slider-thumb,
  .speed-slider::-webkit-slider-thumb,
  .font-size-slider::-webkit-slider-thumb {
    width: 24px;
    height: 24px;
  }
  
  .volume-value,
  .speed-value,
  .font-size-value {
    min-width: 50px;
    font-size: 1rem;
  }
  
  .voice-select,
  .position-select {
    padding: 12px 16px;
    font-size: 1rem;
    border-radius: 8px;
    margin-top: 0.5rem;
  }
  
  .preview-btn {
    margin-top: 1rem;
    padding: 12px 20px;
    font-size: 1rem;
    border-radius: 8px;
    min-height: 44px;
  }
  
  .subtitle-container {
    max-width: 95%;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .subtitle-container.position-bottom {
    bottom: 100px; /* Account for mobile controls */
  }
  
  .subtitle-container.position-top {
    top: 60px; /* Account for mobile header */
  }
  
  .subtitle-content {
    padding: 16px 20px;
    border-radius: 12px;
  }
  
  .original-text {
    font-size: 15px;
    margin-bottom: 6px;
  }
  
  .translated-text {
    font-size: 17px;
    line-height: 1.4;
  }
  
  .settings-toggle-btn {
    width: 56px;
    height: 56px;
    font-size: 20px;
    top: 16px;
    right: 16px;
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  .settings-toggle-btn,
  .close-btn,
  .preview-btn {
    min-height: 44px;
    min-width: 44px;
    touch-action: manipulation;
  }
  
  .settings-toggle-btn:active {
    transform: scale(0.9);
    transition: transform 0.1s;
  }
  
  .toggle-label {
    min-height: 44px;
    align-items: center;
  }
  
  .volume-slider,
  .speed-slider,
  .font-size-slider {
    min-height: 44px;
    padding: 16px 0;
  }
  
  .voice-select,
  .position-select {
    min-height: 44px;
  }
}

/* Landscape orientation on mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .translation-settings-panel {
    flex-direction: row;
  }
  
  .settings-content {
    padding: 1rem;
  }
  
  .setting-group {
    margin-bottom: 1rem;
  }
  
  .subtitle-container.position-bottom {
    bottom: 80px;
  }
  
  .subtitle-container.position-top {
    top: 40px;
  }
}

/* Very small screens */
@media (max-width: 480px) {
  .settings-content {
    padding: 1rem;
  }
  
  .setting-group {
    margin-bottom: 1.25rem;
  }
  
  .subtitle-content {
    padding: 12px 16px;
  }
  
  .original-text {
    font-size: 14px;
  }
  
  .translated-text {
    font-size: 16px;
  }
  
  .settings-toggle-btn {
    width: 48px;
    height: 48px;
    font-size: 18px;
  }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .subtitle-content {
    border: 0.5px solid rgba(255, 255, 255, 0.1);
  }
  
  .translation-settings-panel {
    border: 0.5px solid rgba(0, 0, 0, 0.1);
  }
}
</style>