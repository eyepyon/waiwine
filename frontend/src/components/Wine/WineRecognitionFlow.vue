<template>
  <div class="wine-recognition-flow">
    <!-- Step 1: Camera Interface -->
    <div v-if="currentStep === 'camera'" class="step-container">
      <div class="step-header">
        <h2>{{ $t('wine.capture_label') }}</h2>
        <p>{{ $t('wine.capture_instructions') }}</p>
      </div>
      
      <CameraInterface 
        @photo-captured="onPhotoCaptured"
        @camera-error="onCameraError"
      />
    </div>
    
    <!-- Step 2: Wine Recognition Processing -->
    <div v-if="currentStep === 'processing'" class="step-container">
      <div class="processing-container">
        <div class="processing-animation">
          <div class="wine-glass-icon">🍷</div>
          <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        
        <h3>{{ $t('wine.recognition_loading') }}</h3>
        <p>{{ $t('wine.analyzing_label') }}</p>
        
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${recognitionProgress}%` }"></div>
        </div>
      </div>
    </div>
    
    <!-- Step 3: Wine Recognition Results -->
    <div v-if="currentStep === 'results'" class="step-container">
      <div class="results-header">
        <h2>{{ $t('wine.recognition_results') }}</h2>
      </div>
      
      <!-- Successful Recognition -->
      <div v-if="recognitionResult && recognitionResult.success" class="recognition-success">
        <div class="wine-match">
          <div class="wine-info">
            <h3 class="wine-name">{{ recognitionResult.wine_name }}</h3>
            <div class="wine-details">
              <span v-if="recognitionResult.vintage" class="wine-vintage">
                {{ recognitionResult.vintage }}
              </span>
              <span v-if="recognitionResult.producer" class="wine-producer">
                {{ recognitionResult.producer }}
              </span>
              <span v-if="recognitionResult.region" class="wine-region">
                {{ recognitionResult.region }}
              </span>
            </div>
            
            <div class="confidence-score">
              <span class="confidence-label">{{ $t('wine.confidence') }}:</span>
              <div class="confidence-bar">
                <div 
                  class="confidence-fill" 
                  :style="{ width: `${recognitionResult.confidence_score * 100}%` }"
                ></div>
              </div>
              <span class="confidence-value">
                {{ Math.round(recognitionResult.confidence_score * 100) }}%
              </span>
            </div>
          </div>
        </div>
        
        <!-- Room Information -->
        <div class="room-info" v-if="roomInfo">
          <div class="room-stats">
            <div class="stat-item">
              <i class="icon-users"></i>
              <span>{{ roomInfo.participants_count || 0 }} {{ $t('room.participants') }}</span>
            </div>
            <div class="stat-item">
              <i class="icon-clock"></i>
              <span>{{ $t('room.active_now') }}</span>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="action-buttons">
          <button @click="joinWineRoom" class="join-room-btn" :disabled="joiningRoom">
            <i class="icon-video"></i>
            {{ joiningRoom ? $t('room.joining') : $t('room.join_wine_room') }}
          </button>
          
          <button @click="selectDifferentWine" class="select-different-btn">
            <i class="icon-search"></i>
            {{ $t('wine.select_different') }}
          </button>
        </div>
        
        <!-- Alternative Matches -->
        <div v-if="recognitionResult.matched_wines && recognitionResult.matched_wines.length > 1" 
             class="alternative-matches">
          <h4>{{ $t('wine.other_matches') }}</h4>
          <div class="matches-list">
            <div 
              v-for="wine in recognitionResult.matched_wines.slice(1, 4)" 
              :key="wine.id"
              class="match-item"
              @click="selectAlternativeWine(wine)"
            >
              <div class="match-info">
                <span class="match-name">{{ wine.name }}</span>
                <span class="match-details">{{ wine.producer }} {{ wine.vintage }}</span>
              </div>
              <button class="select-match-btn">
                {{ $t('wine.select') }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recognition Failed -->
      <div v-else class="recognition-failed">
        <div class="failure-icon">❌</div>
        <h3>{{ $t('wine.recognition_failed') }}</h3>
        <p>{{ recognitionResult?.error_message || $t('wine.recognition_error_generic') }}</p>
        
        <div class="failure-actions">
          <button @click="retryRecognition" class="retry-btn">
            <i class="icon-refresh"></i>
            {{ $t('wine.retry_recognition') }}
          </button>
          
          <button @click="manualSelection" class="manual-select-btn">
            <i class="icon-search"></i>
            {{ $t('wine.manual_selection') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Step 4: Manual Wine Selection -->
    <div v-if="currentStep === 'manual'" class="step-container">
      <div class="manual-selection-header">
        <h2>{{ $t('wine.manual_selection') }}</h2>
        <p>{{ $t('wine.manual_selection_instructions') }}</p>
      </div>
      
      <WineSelector 
        @wine-selected="onManualWineSelected"
        @cancel="currentStep = 'camera'"
      />
    </div>
    
    <!-- Error State -->
    <div v-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>{{ $t('common.error') }}</h3>
      <p>{{ error }}</p>
      
      <div class="error-actions">
        <button @click="resetFlow" class="reset-btn">
          {{ $t('wine.start_over') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import CameraInterface from '@/components/Camera/CameraInterface.vue'
import WineSelector from '@/components/Wine/WineSelector.vue'

export default {
  name: 'WineRecognitionFlow',
  components: {
    CameraInterface,
    WineSelector
  },
  setup() {
    const { t } = useI18n()
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Flow state
    const currentStep = ref('camera')
    const error = ref(null)
    
    // Recognition state
    const capturedPhoto = ref(null)
    const recognitionResult = ref(null)
    const recognitionProgress = ref(0)
    const roomInfo = ref(null)
    const joiningRoom = ref(false)
    
    // Methods
    const onPhotoCaptured = async (photoData) => {
      capturedPhoto.value = photoData
      currentStep.value = 'processing'
      
      try {
        await processWineRecognition(photoData.blob)
      } catch (err) {
        error.value = err.message
        console.error('Wine recognition error:', err)
      }
    }
    
    const processWineRecognition = async (imageBlob) => {
      try {
        // Simulate progress
        const progressInterval = setInterval(() => {
          recognitionProgress.value = Math.min(recognitionProgress.value + 10, 90)
        }, 200)
        
        // Create form data for image upload
        const formData = new FormData()
        formData.append('image', imageBlob, 'wine-label.jpg')
        
        // Call wine recognition API
        const response = await fetch('/api/wines/recognize', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          },
          body: formData
        })
        
        clearInterval(progressInterval)
        recognitionProgress.value = 100
        
        if (!response.ok) {
          throw new Error(`Recognition failed: ${response.statusText}`)
        }
        
        const result = await response.json()
        recognitionResult.value = result
        
        // If recognition was successful, get room information
        if (result.success && result.wine_id) {
          await fetchRoomInfo(result.wine_id)
        }
        
        // Move to results step after a brief delay
        setTimeout(() => {
          currentStep.value = 'results'
        }, 500)
        
      } catch (err) {
        recognitionResult.value = {
          success: false,
          error_message: err.message
        }
        currentStep.value = 'results'
        throw err
      }
    }
    
    const fetchRoomInfo = async (wineId) => {
      try {
        const response = await fetch(`/api/rooms/wine/${wineId}`, {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          roomInfo.value = data.rooms[0] || { participants_count: 0 }
        }
      } catch (err) {
        console.error('Failed to fetch room info:', err)
        // Don't fail the whole flow for room info
        roomInfo.value = { participants_count: 0 }
      }
    }
    
    const joinWineRoom = async () => {
      if (!recognitionResult.value?.wine_id) return
      
      joiningRoom.value = true
      
      try {
        // Navigate to video room with wine ID
        await router.push({
          name: 'VideoRoom',
          params: { wineId: recognitionResult.value.wine_id }
        })
      } catch (err) {
        error.value = t('room.join_failed')
        console.error('Failed to join room:', err)
      } finally {
        joiningRoom.value = false
      }
    }
    
    const selectDifferentWine = () => {
      currentStep.value = 'manual'
    }
    
    const selectAlternativeWine = async (wine) => {
      // Update recognition result with selected wine
      recognitionResult.value = {
        ...recognitionResult.value,
        wine_id: wine.id,
        wine_name: wine.name,
        producer: wine.producer,
        vintage: wine.vintage,
        region: wine.region
      }
      
      // Fetch room info for the selected wine
      await fetchRoomInfo(wine.id)
    }
    
    const retryRecognition = () => {
      if (capturedPhoto.value) {
        currentStep.value = 'processing'
        recognitionProgress.value = 0
        processWineRecognition(capturedPhoto.value.blob)
      } else {
        currentStep.value = 'camera'
      }
    }
    
    const manualSelection = () => {
      currentStep.value = 'manual'
    }
    
    const onManualWineSelected = async (wine) => {
      // Set recognition result with manually selected wine
      recognitionResult.value = {
        success: true,
        wine_id: wine.id,
        wine_name: wine.name,
        producer: wine.producer,
        vintage: wine.vintage,
        region: wine.region,
        confidence_score: 1.0, // Manual selection is 100% confident
        matched_wines: [wine]
      }
      
      // Fetch room info
      await fetchRoomInfo(wine.id)
      
      currentStep.value = 'results'
    }
    
    const onCameraError = (err) => {
      error.value = t('camera.camera_error')
      console.error('Camera error:', err)
    }
    
    const resetFlow = () => {
      currentStep.value = 'camera'
      error.value = null
      capturedPhoto.value = null
      recognitionResult.value = null
      recognitionProgress.value = 0
      roomInfo.value = null
      joiningRoom.value = false
    }
    
    return {
      // State
      currentStep,
      error,
      capturedPhoto,
      recognitionResult,
      recognitionProgress,
      roomInfo,
      joiningRoom,
      
      // Methods
      onPhotoCaptured,
      joinWineRoom,
      selectDifferentWine,
      selectAlternativeWine,
      retryRecognition,
      manualSelection,
      onManualWineSelected,
      onCameraError,
      resetFlow
    }
  }
}
</script>

<style scoped>
.wine-recognition-flow {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.step-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.step-header {
  text-align: center;
  margin-bottom: 2rem;
}

.step-header h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.step-header p {
  color: #666;
  margin: 0;
}

/* Processing Step */
.processing-container {
  text-align: center;
  padding: 2rem 0;
}

.processing-animation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.wine-glass-icon {
  font-size: 3rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.loading-dots {
  display: flex;
  gap: 0.25rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #007bff;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #28a745);
  transition: width 0.3s ease;
}

/* Results Step */
.results-header {
  text-align: center;
  margin-bottom: 2rem;
}

.recognition-success {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.wine-match {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
}

.wine-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.wine-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.wine-vintage,
.wine-producer,
.wine-region {
  color: #666;
  font-size: 0.9rem;
}

.confidence-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-label {
  font-weight: 500;
  color: #333;
}

.confidence-bar {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #dc3545, #ffc107, #28a745);
  transition: width 0.3s ease;
}

.confidence-value {
  font-weight: 600;
  color: #333;
}

.room-info {
  background: #e3f2fd;
  border-radius: 8px;
  padding: 1rem;
}

.room-stats {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #1976d2;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.join-room-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.join-room-btn:hover:not(:disabled) {
  background: #218838;
}

.join-room-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-different-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.select-different-btn:hover {
  background: #545b62;
}

.alternative-matches {
  border-top: 1px solid #dee2e6;
  padding-top: 1.5rem;
}

.alternative-matches h4 {
  margin: 0 0 1rem 0;
  color: #333;
}

.matches-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.match-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.match-item:hover {
  background: #e9ecef;
}

.match-info {
  display: flex;
  flex-direction: column;
}

.match-name {
  font-weight: 500;
  color: #333;
}

.match-details {
  font-size: 0.875rem;
  color: #666;
}

.select-match-btn {
  padding: 0.25rem 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
}

/* Recognition Failed */
.recognition-failed {
  text-align: center;
  padding: 2rem 0;
}

.failure-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.failure-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.retry-btn,
.manual-select-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn {
  background: #007bff;
  color: white;
}

.retry-btn:hover {
  background: #0056b3;
}

.manual-select-btn {
  background: #6c757d;
  color: white;
}

.manual-select-btn:hover {
  background: #545b62;
}

/* Error State */
.error-container {
  text-align: center;
  padding: 2rem;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-actions {
  margin-top: 2rem;
}

.reset-btn {
  padding: 0.75rem 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.reset-btn:hover {
  background: #c82333;
}

/* Responsive Design */
@media (max-width: 768px) {
  .wine-recognition-flow {
    padding: 0.5rem;
  }
  
  .step-container {
    padding: 1rem;
  }
  
  .action-buttons,
  .failure-actions {
    flex-direction: column;
  }
  
  .wine-details {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .room-stats {
    flex-direction: column;
    align-items: center;
  }
}
</style>