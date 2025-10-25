<template>
  <div class="video-room">
    <!-- Room Header -->
    <div class="room-header">
      <div class="room-info">
        <h2 class="room-title">{{ $t('room.title') }}</h2>
        <div class="wine-info" v-if="wineInfo">
          <img 
            v-if="wineInfo.image_url" 
            :src="wineInfo.image_url" 
            :alt="wineInfo.name"
            class="wine-image"
          />
          <div class="wine-details">
            <h3 class="wine-name">{{ getLocalizedWineName(wineInfo) }}</h3>
            <p class="wine-vintage" v-if="wineInfo.vintage">{{ wineInfo.vintage }}</p>
            <p class="wine-region" v-if="wineInfo.region">{{ wineInfo.region }}</p>
          </div>
        </div>
      </div>
      
      <div class="room-controls">
        <div class="participant-count">
          <i class="icon-users"></i>
          <span>{{ participantCount }} {{ $t('room.participants') }}</span>
        </div>
        <button 
          @click="leaveRoom" 
          class="btn btn-danger"
          :disabled="isLeaving"
        >
          {{ isLeaving ? $t('room.leaving') : $t('room.leave') }}
        </button>
      </div>
    </div>

    <!-- Video Chat Interface -->
    <div class="video-container" v-if="isConnected">
      <LiveKitRoom
        v-if="roomToken"
        :server-url="serverUrl"
        :token="roomToken"
        :options="roomOptions"
        @connected="onRoomConnected"
        @disconnected="onRoomDisconnected"
        @participant-connected="onParticipantConnected"
        @participant-disconnected="onParticipantDisconnected"
        @error="onRoomError"
      >
        <!-- Translation Overlay -->
        <TranslationOverlay
          :room-id="`wine-${wineId}`"
          :participants="allParticipants"
          @translation-ready="onTranslationReady"
          @translation-error="onTranslationError"
        />
        <!-- Main video grid -->
        <div class="video-grid">
          <!-- Local participant (self) -->
          <div class="video-tile local-video">
            <VideoTrack
              :participant="localParticipant"
              :track-ref="localVideoTrack"
              class="video-element"
            />
            <div class="participant-info">
              <span class="participant-name">{{ $t('room.you') }}</span>
              <div class="participant-controls">
                <button 
                  @click="toggleCamera" 
                  :class="['control-btn', { active: isCameraEnabled }]"
                  :title="$t('room.toggle_camera')"
                >
                  <i :class="isCameraEnabled ? 'icon-camera' : 'icon-camera-off'"></i>
                </button>
                <button 
                  @click="toggleMicrophone" 
                  :class="['control-btn', { active: isMicrophoneEnabled }]"
                  :title="$t('room.toggle_microphone')"
                >
                  <i :class="isMicrophoneEnabled ? 'icon-mic' : 'icon-mic-off'"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Remote participants -->
          <div 
            v-for="participant in remoteParticipants" 
            :key="participant.identity"
            class="video-tile remote-video"
          >
            <VideoTrack
              :participant="participant"
              :track-ref="getVideoTrack(participant)"
              class="video-element"
            />
            <AudioTrack
              :participant="participant"
              :track-ref="getAudioTrack(participant)"
            />
            <div class="participant-info">
              <span class="participant-name">{{ participant.name || participant.identity }}</span>
              <div class="participant-status">
                <i 
                  v-if="isParticipantSpeaking(participant)" 
                  class="icon-volume speaking"
                ></i>
                <i 
                  v-if="!hasVideo(participant)" 
                  class="icon-camera-off"
                ></i>
                <i 
                  v-if="!hasAudio(participant)" 
                  class="icon-mic-off"
                ></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Room controls -->
        <div class="room-bottom-controls">
          <div class="media-controls">
            <button 
              @click="toggleCamera" 
              :class="['media-btn', { active: isCameraEnabled }]"
            >
              <i :class="isCameraEnabled ? 'icon-camera' : 'icon-camera-off'"></i>
              <span>{{ $t('room.camera') }}</span>
            </button>
            
            <button 
              @click="toggleMicrophone" 
              :class="['media-btn', { active: isMicrophoneEnabled }]"
            >
              <i :class="isMicrophoneEnabled ? 'icon-mic' : 'icon-mic-off'"></i>
              <span>{{ $t('room.microphone') }}</span>
            </button>
            
            <button 
              @click="toggleScreenShare" 
              :class="['media-btn', { active: isScreenSharing }]"
            >
              <i class="icon-screen-share"></i>
              <span>{{ $t('room.screen_share') }}</span>
            </button>
          </div>
          
          <div class="additional-controls">
            <button 
              @click="toggleParticipantsList" 
              class="control-btn"
            >
              <i class="icon-users"></i>
              <span>{{ participantCount }}</span>
            </button>
            
            <button 
              @click="toggleTranslation" 
              :class="['control-btn', { active: isTranslationEnabled }]"
              :title="$t('translation.settings')"
            >
              <i class="icon-translate"></i>
            </button>
            
            <button 
              @click="toggleSettings" 
              class="control-btn"
            >
              <i class="icon-settings"></i>
            </button>
          </div>
        </div>
      </LiveKitRoom>
    </div>

    <!-- Loading state -->
    <div v-else-if="isConnecting" class="loading-container">
      <div class="loading-spinner"></div>
      <p>{{ $t('room.connecting') }}</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <div class="error-message">
        <i class="icon-alert"></i>
        <h3>{{ $t('room.connection_error') }}</h3>
        <p>{{ error }}</p>
        <button @click="retryConnection" class="btn btn-primary">
          {{ $t('room.retry') }}
        </button>
      </div>
    </div>

    <!-- Participants sidebar -->
    <ParticipantsList 
      v-if="showParticipantsList"
      :participants="allParticipants"
      :local-participant="localParticipant"
      @close="toggleParticipantsList"
    />

    <!-- Settings modal -->
    <RoomSettings 
      v-if="showSettings"
      @close="toggleSettings"
      @settings-changed="onSettingsChanged"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  LiveKitRoom, 
  VideoTrack, 
  AudioTrack,
  useRoom,
  useLocalParticipant,
  useRemoteParticipants,
  useTracks
} from '@livekit/components-vue'
import { Track, Room, RoomEvent } from 'livekit-client'
import { useAuthStore } from '@/stores/auth'
import ParticipantsList from './ParticipantsList.vue'
import RoomSettings from './RoomSettings.vue'
import TranslationOverlay from '../Translation/TranslationOverlay.vue'

export default {
  name: 'VideoRoom',
  components: {
    LiveKitRoom,
    VideoTrack,
    AudioTrack,
    ParticipantsList,
    RoomSettings,
    TranslationOverlay
  },
  props: {
    wineId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const { t } = useI18n()
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Room connection state
    const isConnecting = ref(false)
    const isConnected = ref(false)
    const isLeaving = ref(false)
    const error = ref(null)
    const roomToken = ref(null)
    const serverUrl = ref('')
    
    // Wine information
    const wineInfo = ref(null)
    
    // Room and participant state
    const room = ref(null)
    const localParticipant = ref(null)
    const remoteParticipants = ref([])
    const participantCount = computed(() => {
      return 1 + remoteParticipants.value.length // 1 for local participant
    })
    
    // Media controls state
    const isCameraEnabled = ref(true)
    const isMicrophoneEnabled = ref(true)
    const isScreenSharing = ref(false)
    
    // UI state
    const showParticipantsList = ref(false)
    const showSettings = ref(false)
    
    // Translation state
    const isTranslationEnabled = ref(false)
    const translationReady = ref(false)
    
    // Room options
    const roomOptions = {
      adaptiveStream: true,
      dynacast: true,
      videoCaptureDefaults: {
        resolution: {
          width: 1280,
          height: 720
        }
      }
    }
    
    // Computed properties
    const allParticipants = computed(() => {
      const participants = [...remoteParticipants.value]
      if (localParticipant.value) {
        participants.unshift(localParticipant.value)
      }
      return participants
    })
    
    const localVideoTrack = computed(() => {
      if (!localParticipant.value) return null
      return localParticipant.value.getTrack(Track.Source.Camera)
    })
    
    // Methods
    const joinRoom = async () => {
      try {
        isConnecting.value = true
        error.value = null
        
        const response = await fetch('/api/rooms/join', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            wine_id: props.wineId
          })
        })
        
        if (!response.ok) {
          throw new Error(`Failed to join room: ${response.statusText}`)
        }
        
        const roomData = await response.json()
        roomToken.value = roomData.access_token
        serverUrl.value = roomData.livekit_url
        
        // Fetch wine information
        await fetchWineInfo()
        
      } catch (err) {
        error.value = err.message
        console.error('Error joining room:', err)
      } finally {
        isConnecting.value = false
      }
    }
    
    const fetchWineInfo = async () => {
      try {
        const response = await fetch(`/api/wines/${props.wineId}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          wineInfo.value = await response.json()
        }
      } catch (err) {
        console.error('Error fetching wine info:', err)
      }
    }
    
    const leaveRoom = async () => {
      try {
        isLeaving.value = true
        
        if (room.value) {
          await room.value.disconnect()
        }
        
        // Notify backend
        await fetch('/api/rooms/leave', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            room_name: `wine-${props.wineId}`
          })
        })
        
        // Navigate back to home
        router.push('/')
        
      } catch (err) {
        console.error('Error leaving room:', err)
      } finally {
        isLeaving.value = false
      }
    }
    
    const retryConnection = () => {
      error.value = null
      joinRoom()
    }
    
    // Media control methods
    const toggleCamera = async () => {
      if (!localParticipant.value) return
      
      try {
        await localParticipant.value.setCameraEnabled(!isCameraEnabled.value)
        isCameraEnabled.value = !isCameraEnabled.value
      } catch (err) {
        console.error('Error toggling camera:', err)
      }
    }
    
    const toggleMicrophone = async () => {
      if (!localParticipant.value) return
      
      try {
        await localParticipant.value.setMicrophoneEnabled(!isMicrophoneEnabled.value)
        isMicrophoneEnabled.value = !isMicrophoneEnabled.value
      } catch (err) {
        console.error('Error toggling microphone:', err)
      }
    }
    
    const toggleScreenShare = async () => {
      if (!localParticipant.value) return
      
      try {
        await localParticipant.value.setScreenShareEnabled(!isScreenSharing.value)
        isScreenSharing.value = !isScreenSharing.value
      } catch (err) {
        console.error('Error toggling screen share:', err)
      }
    }
    
    // UI control methods
    const toggleParticipantsList = () => {
      showParticipantsList.value = !showParticipantsList.value
    }
    
    const toggleSettings = () => {
      showSettings.value = !showSettings.value
    }
    
    const toggleTranslation = () => {
      isTranslationEnabled.value = !isTranslationEnabled.value
    }
    
    // Utility methods
    const getLocalizedWineName = (wine) => {
      if (!wine) return ''
      
      const currentLocale = t('locale')
      if (wine.name_translations && wine.name_translations[currentLocale]) {
        return wine.name_translations[currentLocale]
      }
      return wine.name
    }
    
    const getVideoTrack = (participant) => {
      return participant.getTrack(Track.Source.Camera)
    }
    
    const getAudioTrack = (participant) => {
      return participant.getTrack(Track.Source.Microphone)
    }
    
    const hasVideo = (participant) => {
      const track = participant.getTrack(Track.Source.Camera)
      return track && !track.isMuted
    }
    
    const hasAudio = (participant) => {
      const track = participant.getTrack(Track.Source.Microphone)
      return track && !track.isMuted
    }
    
    const isParticipantSpeaking = (participant) => {
      return participant.isSpeaking
    }
    
    // Event handlers
    const onRoomConnected = (roomInstance) => {
      console.log('Connected to room:', roomInstance.name)
      room.value = roomInstance
      isConnected.value = true
      localParticipant.value = roomInstance.localParticipant
    }
    
    const onRoomDisconnected = () => {
      console.log('Disconnected from room')
      isConnected.value = false
      room.value = null
      localParticipant.value = null
      remoteParticipants.value = []
    }
    
    const onParticipantConnected = (participant) => {
      console.log('Participant connected:', participant.identity)
      remoteParticipants.value.push(participant)
    }
    
    const onParticipantDisconnected = (participant) => {
      console.log('Participant disconnected:', participant.identity)
      const index = remoteParticipants.value.findIndex(p => p.identity === participant.identity)
      if (index > -1) {
        remoteParticipants.value.splice(index, 1)
      }
    }
    
    const onRoomError = (error) => {
      console.error('Room error:', error)
      error.value = error.message
    }
    
    const onSettingsChanged = (settings) => {
      // Handle settings changes
      console.log('Settings changed:', settings)
    }
    
    const onTranslationReady = () => {
      translationReady.value = true
      console.log('Translation service ready')
    }
    
    const onTranslationError = (error) => {
      console.error('Translation error:', error)
      translationReady.value = false
    }
    
    // Mobile-specific methods
    const setupMobileOptimizations = () => {
      // Prevent zoom on double tap for video elements
      const videoElements = document.querySelectorAll('.video-element')
      videoElements.forEach(video => {
        video.addEventListener('touchstart', (e) => {
          e.preventDefault()
        })
      })
      
      // Optimize for mobile performance
      if (window.innerWidth <= 768) {
        // Reduce video quality for mobile
        roomOptions.videoCaptureDefaults = {
          resolution: {
            width: 640,
            height: 480
          },
          frameRate: 15
        }
      }
      
      // Handle orientation changes
      window.addEventListener('orientationchange', () => {
        setTimeout(() => {
          // Trigger layout recalculation
          window.dispatchEvent(new Event('resize'))
        }, 100)
      })
    }
    
    // Lifecycle
    onMounted(() => {
      setupMobileOptimizations()
      joinRoom()
    })
    
    onUnmounted(() => {
      if (room.value) {
        room.value.disconnect()
      }
    })
    
    return {
      // State
      isConnecting,
      isConnected,
      isLeaving,
      error,
      roomToken,
      serverUrl,
      wineInfo,
      room,
      localParticipant,
      remoteParticipants,
      participantCount,
      isCameraEnabled,
      isMicrophoneEnabled,
      isScreenSharing,
      showParticipantsList,
      showSettings,
      isTranslationEnabled,
      translationReady,
      roomOptions,
      allParticipants,
      localVideoTrack,
      
      // Methods
      leaveRoom,
      retryConnection,
      toggleCamera,
      toggleMicrophone,
      toggleScreenShare,
      toggleParticipantsList,
      toggleSettings,
      toggleTranslation,
      getLocalizedWineName,
      getVideoTrack,
      getAudioTrack,
      hasVideo,
      hasAudio,
      isParticipantSpeaking,
      
      // Event handlers
      onRoomConnected,
      onRoomDisconnected,
      onParticipantConnected,
      onParticipantDisconnected,
      onRoomError,
      onSettingsChanged,
      onTranslationReady,
      onTranslationError
    }
  }
}
</script>

<style scoped>
.video-room {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: white;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #2a2a2a;
  border-bottom: 1px solid #3a3a3a;
}

.room-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.room-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.wine-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.wine-image {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.wine-details {
  display: flex;
  flex-direction: column;
}

.wine-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
}

.wine-vintage,
.wine-region {
  margin: 0;
  font-size: 0.875rem;
  color: #ccc;
}

.room-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.participant-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ccc;
}

.video-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.video-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.video-tile {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 16/9;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.local-video {
  border: 2px solid #4CAF50;
}

.participant-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.participant-name {
  font-weight: 500;
}

.participant-controls,
.participant-status {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.control-btn:hover {
  background: rgba(255,255,255,0.3);
}

.control-btn.active {
  background: #4CAF50;
}

.room-bottom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #2a2a2a;
  border-top: 1px solid #3a3a3a;
}

.media-controls {
  display: flex;
  gap: 1rem;
}

.media-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.media-btn:hover {
  background: rgba(255,255,255,0.2);
}

.media-btn.active {
  background: #4CAF50;
}

.additional-controls {
  display: flex;
  gap: 0.5rem;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #3a3a3a;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  max-width: 400px;
}

.error-message h3 {
  color: #f44336;
  margin-bottom: 0.5rem;
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

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #da190b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.speaking {
  color: #4CAF50;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Mobile-responsive design */
@media (max-width: 768px) {
  .video-room {
    height: 100vh;
    overflow: hidden;
  }
  
  .room-header {
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    min-height: auto;
  }
  
  .room-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    width: 100%;
  }
  
  .room-title {
    font-size: 1.25rem;
  }
  
  .wine-info {
    align-self: stretch;
    justify-content: flex-start;
  }
  
  .wine-image {
    width: 32px;
    height: 32px;
  }
  
  .wine-name {
    font-size: 0.9rem;
  }
  
  .wine-vintage,
  .wine-region {
    font-size: 0.8rem;
  }
  
  .room-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .participant-count {
    font-size: 0.9rem;
  }
  
  .video-container {
    flex: 1;
    min-height: 0;
  }
  
  .video-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 0.5rem;
    height: 100%;
    overflow-y: auto;
  }
  
  .video-tile {
    aspect-ratio: 16/9;
    min-height: 200px;
  }
  
  .local-video {
    order: -1;
  }
  
  .participant-info {
    padding: 0.75rem;
  }
  
  .participant-name {
    font-size: 0.9rem;
  }
  
  .control-btn {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .room-bottom-controls {
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #2a2a2a;
  }
  
  .media-controls {
    justify-content: space-around;
    gap: 0.5rem;
  }
  
  .media-btn {
    flex: 1;
    max-width: 80px;
    padding: 0.75rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .media-btn i {
    font-size: 18px;
  }
  
  .additional-controls {
    justify-content: center;
    gap: 1rem;
  }
  
  .additional-controls .control-btn {
    width: 44px;
    height: 44px;
    font-size: 18px;
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  .media-btn,
  .control-btn,
  .btn {
    min-height: 44px;
    touch-action: manipulation;
  }
  
  .media-btn:active {
    transform: scale(0.95);
    transition: transform 0.1s;
  }
  
  .control-btn:active {
    transform: scale(0.9);
    transition: transform 0.1s;
  }
  
  .video-tile {
    touch-action: pan-y;
  }
}

/* Landscape orientation on mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .room-header {
    flex-direction: row;
    padding: 0.5rem 1rem;
  }
  
  .room-info {
    flex-direction: row;
    align-items: center;
  }
  
  .room-title {
    font-size: 1.1rem;
  }
  
  .video-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    padding: 0.25rem;
  }
  
  .video-tile {
    min-height: 140px;
  }
  
  .room-bottom-controls {
    flex-direction: row;
    justify-content: space-between;
    padding: 0.5rem 1rem;
  }
  
  .media-controls {
    gap: 0.75rem;
  }
  
  .media-btn {
    flex: none;
    min-width: 60px;
  }
}

/* Very small screens */
@media (max-width: 480px) {
  .room-header {
    padding: 0.5rem;
  }
  
  .room-title {
    font-size: 1.1rem;
  }
  
  .video-grid {
    padding: 0.25rem;
  }
  
  .video-tile {
    min-height: 180px;
  }
  
  .participant-info {
    padding: 0.5rem;
  }
  
  .media-btn span {
    display: none;
  }
  
  .media-btn {
    min-width: 50px;
  }
}
</style>