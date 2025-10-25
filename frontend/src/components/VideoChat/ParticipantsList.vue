<template>
  <div class="participants-sidebar">
    <div class="sidebar-header">
      <h3>{{ $t('room.participants') }} ({{ participants.length }})</h3>
      <button @click="$emit('close')" class="close-btn">
        <i class="icon-close"></i>
      </button>
    </div>
    
    <div class="participants-list">
      <div 
        v-for="participant in participants" 
        :key="participant.identity"
        :class="['participant-item', { 
          'local': participant === localParticipant,
          'speaking': participant.isSpeaking 
        }]"
      >
        <div class="participant-avatar">
          <img 
            v-if="getParticipantAvatar(participant)" 
            :src="getParticipantAvatar(participant)"
            :alt="getParticipantName(participant)"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            {{ getParticipantInitials(participant) }}
          </div>
          
          <!-- Speaking indicator -->
          <div v-if="participant.isSpeaking" class="speaking-indicator">
            <i class="icon-volume"></i>
          </div>
        </div>
        
        <div class="participant-details">
          <div class="participant-name">
            {{ getParticipantName(participant) }}
            <span v-if="participant === localParticipant" class="you-label">
              ({{ $t('room.you') }})
            </span>
          </div>
          
          <div class="participant-status">
            <div class="media-status">
              <i 
                :class="[
                  'status-icon',
                  hasVideo(participant) ? 'icon-camera' : 'icon-camera-off',
                  { 'disabled': !hasVideo(participant) }
                ]"
                :title="hasVideo(participant) ? $t('room.camera_on') : $t('room.camera_off')"
              ></i>
              <i 
                :class="[
                  'status-icon',
                  hasAudio(participant) ? 'icon-mic' : 'icon-mic-off',
                  { 'disabled': !hasAudio(participant) }
                ]"
                :title="hasAudio(participant) ? $t('room.mic_on') : $t('room.mic_off')"
              ></i>
            </div>
            
            <div class="connection-status">
              <div 
                :class="['connection-indicator', getConnectionQuality(participant)]"
                :title="$t(`room.connection_${getConnectionQuality(participant)}`)"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- Participant actions (for remote participants) -->
        <div v-if="participant !== localParticipant" class="participant-actions">
          <button 
            @click="toggleParticipantAudio(participant)"
            :class="['action-btn', { 'muted': isParticipantMuted(participant) }]"
            :title="isParticipantMuted(participant) ? $t('room.unmute_participant') : $t('room.mute_participant')"
          >
            <i :class="isParticipantMuted(participant) ? 'icon-volume-off' : 'icon-volume'"></i>
          </button>
          
          <button 
            @click="pinParticipant(participant)"
            :class="['action-btn', { 'active': isPinned(participant) }]"
            :title="$t('room.pin_participant')"
          >
            <i class="icon-pin"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Room statistics -->
    <div class="room-stats">
      <div class="stat-item">
        <i class="icon-clock"></i>
        <span>{{ formatDuration(roomDuration) }}</span>
      </div>
      
      <div class="stat-item">
        <i class="icon-signal"></i>
        <span>{{ $t('room.quality') }}: {{ overallQuality }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Track } from 'livekit-client'

export default {
  name: 'ParticipantsList',
  props: {
    participants: {
      type: Array,
      required: true
    },
    localParticipant: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'participant-muted', 'participant-pinned'],
  setup(props, { emit }) {
    const { t } = useI18n()
    
    // State
    const mutedParticipants = ref(new Set())
    const pinnedParticipant = ref(null)
    const roomStartTime = ref(Date.now())
    const roomDuration = ref(0)
    
    // Timer for room duration
    let durationTimer = null
    
    // Computed properties
    const overallQuality = computed(() => {
      const qualities = props.participants.map(p => getConnectionQuality(p))
      const avgQuality = qualities.reduce((sum, q) => {
        const qualityMap = { excellent: 4, good: 3, fair: 2, poor: 1 }
        return sum + (qualityMap[q] || 1)
      }, 0) / qualities.length
      
      if (avgQuality >= 3.5) return t('room.excellent')
      if (avgQuality >= 2.5) return t('room.good')
      if (avgQuality >= 1.5) return t('room.fair')
      return t('room.poor')
    })
    
    // Methods
    const getParticipantName = (participant) => {
      return participant.name || participant.identity || t('room.unknown_user')
    }
    
    const getParticipantAvatar = (participant) => {
      // In a real implementation, you might get this from user metadata
      return participant.metadata?.avatar || null
    }
    
    const getParticipantInitials = (participant) => {
      const name = getParticipantName(participant)
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }
    
    const hasVideo = (participant) => {
      const track = participant.getTrack(Track.Source.Camera)
      return track && !track.isMuted
    }
    
    const hasAudio = (participant) => {
      const track = participant.getTrack(Track.Source.Microphone)
      return track && !track.isMuted
    }
    
    const getConnectionQuality = (participant) => {
      // In a real implementation, you would get this from LiveKit's connection quality API
      // For now, return a mock quality based on participant state
      if (!participant.tracks || participant.tracks.size === 0) {
        return 'poor'
      }
      
      // Mock quality calculation
      const hasGoodVideo = hasVideo(participant)
      const hasGoodAudio = hasAudio(participant)
      
      if (hasGoodVideo && hasGoodAudio) return 'excellent'
      if (hasGoodVideo || hasGoodAudio) return 'good'
      return 'fair'
    }
    
    const isParticipantMuted = (participant) => {
      return mutedParticipants.value.has(participant.identity)
    }
    
    const isPinned = (participant) => {
      return pinnedParticipant.value === participant.identity
    }
    
    const toggleParticipantAudio = (participant) => {
      const isMuted = isParticipantMuted(participant)
      
      if (isMuted) {
        mutedParticipants.value.delete(participant.identity)
      } else {
        mutedParticipants.value.add(participant.identity)
      }
      
      emit('participant-muted', {
        participant,
        muted: !isMuted
      })
    }
    
    const pinParticipant = (participant) => {
      const currentlyPinned = pinnedParticipant.value
      
      if (currentlyPinned === participant.identity) {
        pinnedParticipant.value = null
      } else {
        pinnedParticipant.value = participant.identity
      }
      
      emit('participant-pinned', {
        participant,
        pinned: pinnedParticipant.value === participant.identity
      })
    }
    
    const formatDuration = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      }
      return `${minutes}:${secs.toString().padStart(2, '0')}`
    }
    
    const updateDuration = () => {
      roomDuration.value = Math.floor((Date.now() - roomStartTime.value) / 1000)
    }
    
    // Lifecycle
    onMounted(() => {
      durationTimer = setInterval(updateDuration, 1000)
    })
    
    onUnmounted(() => {
      if (durationTimer) {
        clearInterval(durationTimer)
      }
    })
    
    return {
      // State
      mutedParticipants,
      pinnedParticipant,
      roomDuration,
      overallQuality,
      
      // Methods
      getParticipantName,
      getParticipantAvatar,
      getParticipantInitials,
      hasVideo,
      hasAudio,
      getConnectionQuality,
      isParticipantMuted,
      isPinned,
      toggleParticipantAudio,
      pinParticipant,
      formatDuration
    }
  }
}
</script>

<style scoped>
.participants-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 320px;
  height: 100vh;
  background: #2a2a2a;
  border-left: 1px solid #3a3a3a;
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #3a3a3a;
}

.sidebar-header h3 {
  margin: 0;
  color: white;
  font-size: 1.125rem;
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

.participants-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.participant-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  transition: background-color 0.2s;
  border-left: 3px solid transparent;
}

.participant-item:hover {
  background: rgba(255,255,255,0.05);
}

.participant-item.local {
  border-left-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.participant-item.speaking {
  border-left-color: #2196F3;
  background: rgba(33, 150, 243, 0.1);
}

.participant-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #4CAF50;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}

.speaking-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 16px;
  height: 16px;
  background: #2196F3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #2a2a2a;
}

.speaking-indicator i {
  font-size: 8px;
  color: white;
}

.participant-details {
  flex: 1;
  min-width: 0;
}

.participant-name {
  color: white;
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.you-label {
  color: #4CAF50;
  font-weight: 400;
}

.participant-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.media-status {
  display: flex;
  gap: 0.25rem;
}

.status-icon {
  font-size: 0.75rem;
  color: #4CAF50;
}

.status-icon.disabled {
  color: #666;
}

.connection-status {
  display: flex;
  align-items: center;
}

.connection-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.connection-indicator.excellent {
  background: #4CAF50;
}

.connection-indicator.good {
  background: #8BC34A;
}

.connection-indicator.fair {
  background: #FF9800;
}

.connection-indicator.poor {
  background: #f44336;
}

.participant-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

.action-btn.active {
  background: #4CAF50;
  color: white;
}

.action-btn.muted {
  background: #f44336;
  color: white;
}

.room-stats {
  padding: 1rem;
  border-top: 1px solid #3a3a3a;
  background: rgba(0,0,0,0.2);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ccc;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-item i {
  font-size: 0.75rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .participants-sidebar {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
}
</style>