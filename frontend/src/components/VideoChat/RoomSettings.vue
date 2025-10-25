<template>
  <div class="settings-modal-overlay" @click="closeModal">
    <div class="settings-modal" @click.stop>
      <div class="modal-header">
        <h3>{{ $t('room.settings') }}</h3>
        <button @click="$emit('close')" class="close-btn">
          <i class="icon-close"></i>
        </button>
      </div>
      
      <div class="modal-content">
        <!-- Video Settings -->
        <div class="settings-section">
          <h4>{{ $t('room.video_settings') }}</h4>
          
          <div class="setting-item">
            <label>{{ $t('room.camera_device') }}</label>
            <select v-model="selectedCamera" @change="onCameraChange">
              <option value="">{{ $t('room.select_camera') }}</option>
              <option 
                v-for="device in videoDevices" 
                :key="device.deviceId"
                :value="device.deviceId"
              >
                {{ device.label || `Camera ${device.deviceId.slice(0, 8)}` }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>{{ $t('room.video_quality') }}</label>
            <select v-model="videoQuality" @change="onVideoQualityChange">
              <option value="low">{{ $t('room.quality_low') }} (480p)</option>
              <option value="medium">{{ $t('room.quality_medium') }} (720p)</option>
              <option value="high">{{ $t('room.quality_high') }} (1080p)</option>
            </select>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="enableVideoProcessing"
                @change="onVideoProcessingChange"
              />
              <span>{{ $t('room.enable_video_processing') }}</span>
            </label>
          </div>
        </div>
        
        <!-- Audio Settings -->
        <div class="settings-section">
          <h4>{{ $t('room.audio_settings') }}</h4>
          
          <div class="setting-item">
            <label>{{ $t('room.microphone_device') }}</label>
            <select v-model="selectedMicrophone" @change="onMicrophoneChange">
              <option value="">{{ $t('room.select_microphone') }}</option>
              <option 
                v-for="device in audioDevices" 
                :key="device.deviceId"
                :value="device.deviceId"
              >
                {{ device.label || `Microphone ${device.deviceId.slice(0, 8)}` }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>{{ $t('room.speaker_device') }}</label>
            <select v-model="selectedSpeaker" @change="onSpeakerChange">
              <option value="">{{ $t('room.select_speaker') }}</option>
              <option 
                v-for="device in outputDevices" 
                :key="device.deviceId"
                :value="device.deviceId"
              >
                {{ device.label || `Speaker ${device.deviceId.slice(0, 8)}` }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>{{ $t('room.microphone_volume') }}</label>
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="microphoneVolume"
                @input="onMicrophoneVolumeChange"
                class="volume-slider"
              />
              <span class="volume-value">{{ microphoneVolume }}%</span>
            </div>
          </div>
          
          <div class="setting-item">
            <label>{{ $t('room.speaker_volume') }}</label>
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="speakerVolume"
                @input="onSpeakerVolumeChange"
                class="volume-slider"
              />
              <span class="volume-value">{{ speakerVolume }}%</span>
            </div>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="enableNoiseSuppression"
                @change="onNoiseSuppressionChange"
              />
              <span>{{ $t('room.enable_noise_suppression') }}</span>
            </label>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="enableEchoCancellation"
                @change="onEchoCancellationChange"
              />
              <span>{{ $t('room.enable_echo_cancellation') }}</span>
            </label>
          </div>
        </div>
        
        <!-- Network Settings -->
        <div class="settings-section">
          <h4>{{ $t('room.network_settings') }}</h4>
          
          <div class="setting-item">
            <label>{{ $t('room.bandwidth_limit') }}</label>
            <select v-model="bandwidthLimit" @change="onBandwidthLimitChange">
              <option value="unlimited">{{ $t('room.unlimited') }}</option>
              <option value="high">{{ $t('room.high_bandwidth') }} (2 Mbps)</option>
              <option value="medium">{{ $t('room.medium_bandwidth') }} (1 Mbps)</option>
              <option value="low">{{ $t('room.low_bandwidth') }} (500 Kbps)</option>
            </select>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="enableAdaptiveStream"
                @change="onAdaptiveStreamChange"
              />
              <span>{{ $t('room.enable_adaptive_stream') }}</span>
            </label>
          </div>
        </div>
        
        <!-- Display Settings -->
        <div class="settings-section">
          <h4>{{ $t('room.display_settings') }}</h4>
          
          <div class="setting-item">
            <label>{{ $t('room.layout_mode') }}</label>
            <select v-model="layoutMode" @change="onLayoutModeChange">
              <option value="grid">{{ $t('room.grid_layout') }}</option>
              <option value="speaker">{{ $t('room.speaker_layout') }}</option>
              <option value="gallery">{{ $t('room.gallery_layout') }}</option>
            </select>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="showParticipantNames"
                @change="onShowParticipantNamesChange"
              />
              <span>{{ $t('room.show_participant_names') }}</span>
            </label>
          </div>
          
          <div class="setting-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="enableFullscreen"
                @change="onFullscreenChange"
              />
              <span>{{ $t('room.enable_fullscreen') }}</span>
            </label>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="resetToDefaults" class="btn btn-secondary">
          {{ $t('room.reset_defaults') }}
        </button>
        <button @click="saveSettings" class="btn btn-primary">
          {{ $t('room.save_settings') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

export default {
  name: 'RoomSettings',
  emits: ['close', 'settings-changed'],
  setup(props, { emit }) {
    const { t } = useI18n()
    
    // Device lists
    const videoDevices = ref([])
    const audioDevices = ref([])
    const outputDevices = ref([])
    
    // Video settings
    const selectedCamera = ref('')
    const videoQuality = ref('medium')
    const enableVideoProcessing = ref(true)
    
    // Audio settings
    const selectedMicrophone = ref('')
    const selectedSpeaker = ref('')
    const microphoneVolume = ref(80)
    const speakerVolume = ref(80)
    const enableNoiseSuppression = ref(true)
    const enableEchoCancellation = ref(true)
    
    // Network settings
    const bandwidthLimit = ref('unlimited')
    const enableAdaptiveStream = ref(true)
    
    // Display settings
    const layoutMode = ref('grid')
    const showParticipantNames = ref(true)
    const enableFullscreen = ref(false)
    
    // Methods
    const loadDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        
        videoDevices.value = devices.filter(device => device.kind === 'videoinput')
        audioDevices.value = devices.filter(device => device.kind === 'audioinput')
        outputDevices.value = devices.filter(device => device.kind === 'audiooutput')
        
        // Set default devices if available
        if (videoDevices.value.length > 0 && !selectedCamera.value) {
          selectedCamera.value = videoDevices.value[0].deviceId
        }
        
        if (audioDevices.value.length > 0 && !selectedMicrophone.value) {
          selectedMicrophone.value = audioDevices.value[0].deviceId
        }
        
        if (outputDevices.value.length > 0 && !selectedSpeaker.value) {
          selectedSpeaker.value = outputDevices.value[0].deviceId
        }
        
      } catch (error) {
        console.error('Error loading devices:', error)
      }
    }
    
    const loadSettings = () => {
      // Load settings from localStorage
      const savedSettings = localStorage.getItem('room-settings')
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings)
          
          // Apply saved settings
          selectedCamera.value = settings.selectedCamera || ''
          videoQuality.value = settings.videoQuality || 'medium'
          enableVideoProcessing.value = settings.enableVideoProcessing ?? true
          
          selectedMicrophone.value = settings.selectedMicrophone || ''
          selectedSpeaker.value = settings.selectedSpeaker || ''
          microphoneVolume.value = settings.microphoneVolume || 80
          speakerVolume.value = settings.speakerVolume || 80
          enableNoiseSuppression.value = settings.enableNoiseSuppression ?? true
          enableEchoCancellation.value = settings.enableEchoCancellation ?? true
          
          bandwidthLimit.value = settings.bandwidthLimit || 'unlimited'
          enableAdaptiveStream.value = settings.enableAdaptiveStream ?? true
          
          layoutMode.value = settings.layoutMode || 'grid'
          showParticipantNames.value = settings.showParticipantNames ?? true
          enableFullscreen.value = settings.enableFullscreen ?? false
          
        } catch (error) {
          console.error('Error loading settings:', error)
        }
      }
    }
    
    const saveSettings = () => {
      const settings = {
        selectedCamera: selectedCamera.value,
        videoQuality: videoQuality.value,
        enableVideoProcessing: enableVideoProcessing.value,
        
        selectedMicrophone: selectedMicrophone.value,
        selectedSpeaker: selectedSpeaker.value,
        microphoneVolume: microphoneVolume.value,
        speakerVolume: speakerVolume.value,
        enableNoiseSuppression: enableNoiseSuppression.value,
        enableEchoCancellation: enableEchoCancellation.value,
        
        bandwidthLimit: bandwidthLimit.value,
        enableAdaptiveStream: enableAdaptiveStream.value,
        
        layoutMode: layoutMode.value,
        showParticipantNames: showParticipantNames.value,
        enableFullscreen: enableFullscreen.value
      }
      
      localStorage.setItem('room-settings', JSON.stringify(settings))
      
      emit('settings-changed', settings)
      emit('close')
    }
    
    const resetToDefaults = () => {
      selectedCamera.value = videoDevices.value[0]?.deviceId || ''
      videoQuality.value = 'medium'
      enableVideoProcessing.value = true
      
      selectedMicrophone.value = audioDevices.value[0]?.deviceId || ''
      selectedSpeaker.value = outputDevices.value[0]?.deviceId || ''
      microphoneVolume.value = 80
      speakerVolume.value = 80
      enableNoiseSuppression.value = true
      enableEchoCancellation.value = true
      
      bandwidthLimit.value = 'unlimited'
      enableAdaptiveStream.value = true
      
      layoutMode.value = 'grid'
      showParticipantNames.value = true
      enableFullscreen.value = false
    }
    
    const closeModal = () => {
      emit('close')
    }
    
    // Event handlers
    const onCameraChange = () => {
      emit('settings-changed', { selectedCamera: selectedCamera.value })
    }
    
    const onVideoQualityChange = () => {
      emit('settings-changed', { videoQuality: videoQuality.value })
    }
    
    const onVideoProcessingChange = () => {
      emit('settings-changed', { enableVideoProcessing: enableVideoProcessing.value })
    }
    
    const onMicrophoneChange = () => {
      emit('settings-changed', { selectedMicrophone: selectedMicrophone.value })
    }
    
    const onSpeakerChange = () => {
      emit('settings-changed', { selectedSpeaker: selectedSpeaker.value })
    }
    
    const onMicrophoneVolumeChange = () => {
      emit('settings-changed', { microphoneVolume: microphoneVolume.value })
    }
    
    const onSpeakerVolumeChange = () => {
      emit('settings-changed', { speakerVolume: speakerVolume.value })
    }
    
    const onNoiseSuppressionChange = () => {
      emit('settings-changed', { enableNoiseSuppression: enableNoiseSuppression.value })
    }
    
    const onEchoCancellationChange = () => {
      emit('settings-changed', { enableEchoCancellation: enableEchoCancellation.value })
    }
    
    const onBandwidthLimitChange = () => {
      emit('settings-changed', { bandwidthLimit: bandwidthLimit.value })
    }
    
    const onAdaptiveStreamChange = () => {
      emit('settings-changed', { enableAdaptiveStream: enableAdaptiveStream.value })
    }
    
    const onLayoutModeChange = () => {
      emit('settings-changed', { layoutMode: layoutMode.value })
    }
    
    const onShowParticipantNamesChange = () => {
      emit('settings-changed', { showParticipantNames: showParticipantNames.value })
    }
    
    const onFullscreenChange = () => {
      emit('settings-changed', { enableFullscreen: enableFullscreen.value })
    }
    
    // Lifecycle
    onMounted(async () => {
      await loadDevices()
      loadSettings()
    })
    
    return {
      // Device lists
      videoDevices,
      audioDevices,
      outputDevices,
      
      // Settings
      selectedCamera,
      videoQuality,
      enableVideoProcessing,
      selectedMicrophone,
      selectedSpeaker,
      microphoneVolume,
      speakerVolume,
      enableNoiseSuppression,
      enableEchoCancellation,
      bandwidthLimit,
      enableAdaptiveStream,
      layoutMode,
      showParticipantNames,
      enableFullscreen,
      
      // Methods
      saveSettings,
      resetToDefaults,
      closeModal,
      
      // Event handlers
      onCameraChange,
      onVideoQualityChange,
      onVideoProcessingChange,
      onMicrophoneChange,
      onSpeakerChange,
      onMicrophoneVolumeChange,
      onSpeakerVolumeChange,
      onNoiseSuppressionChange,
      onEchoCancellationChange,
      onBandwidthLimitChange,
      onAdaptiveStreamChange,
      onLayoutModeChange,
      onShowParticipantNamesChange,
      onFullscreenChange
    }
  }
}
</script>

<style scoped>
.settings-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.settings-modal {
  background: #2a2a2a;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  color: white;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #3a3a3a;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.settings-section {
  margin-bottom: 2rem;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section h4 {
  margin: 0 0 1rem 0;
  color: #4CAF50;
  font-size: 1rem;
  font-weight: 600;
}

.setting-item {
  margin-bottom: 1rem;
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-item label {
  display: block;
  margin-bottom: 0.5rem;
  color: #ccc;
  font-size: 0.875rem;
  font-weight: 500;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.setting-item select {
  width: 100%;
  padding: 0.5rem;
  background: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  color: white;
  font-size: 0.875rem;
}

.setting-item select:focus {
  outline: none;
  border-color: #4CAF50;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.volume-slider {
  flex: 1;
  height: 4px;
  background: #3a3a3a;
  border-radius: 2px;
  outline: none;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
}

.volume-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #4CAF50;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.volume-value {
  min-width: 40px;
  text-align: right;
  color: #ccc;
  font-size: 0.875rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #3a3a3a;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-secondary {
  background: #666;
  color: white;
}

.btn-secondary:hover {
  background: #555;
}

/* Responsive design */
@media (max-width: 768px) {
  .settings-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-content,
  .modal-footer {
    padding: 1rem;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>