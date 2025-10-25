<template>
  <div class="camera-interface">
    <div class="camera-container">
      <video 
        ref="videoElement" 
        autoplay 
        playsinline 
        muted
        :class="{ 'camera-active': cameraActive }"
      ></video>
      
      <canvas 
        ref="canvasElement" 
        style="display: none;"
      ></canvas>
      
      <!-- Camera overlay -->
      <div class="camera-overlay" v-if="cameraActive">
        <div class="viewfinder">
          <div class="corner top-left"></div>
          <div class="corner top-right"></div>
          <div class="corner bottom-left"></div>
          <div class="corner bottom-right"></div>
        </div>
        
        <div class="camera-instructions">
          {{ $t('camera.capture_wine_label') }}
        </div>
      </div>
      
      <!-- Error state -->
      <div class="camera-error" v-if="error">
        <div class="error-icon">📷</div>
        <div class="error-message">{{ error }}</div>
        <button @click="initCamera" class="retry-btn">
          {{ $t('common.retry') }}
        </button>
      </div>
      
      <!-- Loading state -->
      <div class="camera-loading" v-if="loading">
        <div class="loading-spinner"></div>
        <div class="loading-text">{{ $t('common.loading') }}</div>
      </div>
    </div>
    
    <!-- Camera controls -->
    <div class="camera-controls" v-if="cameraActive">
      <button 
        @click="capturePhoto" 
        class="capture-btn"
        :disabled="capturing"
      >
        <span class="capture-icon">📸</span>
        {{ capturing ? $t('common.loading') : $t('camera.capture') }}
      </button>
      
      <button @click="switchCamera" class="switch-camera-btn" v-if="hasMultipleCameras">
        🔄
      </button>
    </div>
    
    <!-- Photo preview -->
    <div class="photo-preview" v-if="capturedPhoto">
      <img :src="capturedPhoto" alt="Captured wine label" />
      
      <div class="preview-controls">
        <button @click="retakePhoto" class="retake-btn">
          {{ $t('camera.retake') }}
        </button>
        
        <button @click="usePhoto" class="use-photo-btn">
          {{ $t('camera.use_photo') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CameraInterface',
  
  emits: ['photo-captured', 'camera-error'],
  
  data() {
    return {
      cameraActive: false,
      loading: false,
      capturing: false,
      error: null,
      capturedPhoto: null,
      stream: null,
      currentFacingMode: 'environment', // 'user' for front camera, 'environment' for back camera
      hasMultipleCameras: false
    }
  },
  
  async mounted() {
    await this.checkCameraAvailability()
    await this.initCamera()
    this.setupMobileGestures()
  },
  
  beforeUnmount() {
    this.stopCamera()
  },
  
  methods: {
    async checkCameraAvailability() {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoDevices = devices.filter(device => device.kind === 'videoinput')
        this.hasMultipleCameras = videoDevices.length > 1
      } catch (err) {
        console.warn('Could not enumerate devices:', err)
      }
    },
    
    async initCamera() {
      this.loading = true
      this.error = null
      
      try {
        // Stop existing stream
        this.stopCamera()
        
        // Request camera access
        const constraints = {
          video: {
            facingMode: this.currentFacingMode,
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          }
        }
        
        this.stream = await navigator.mediaDevices.getUserMedia(constraints)
        
        // Attach stream to video element
        if (this.$refs.videoElement) {
          this.$refs.videoElement.srcObject = this.stream
        }
        
        this.cameraActive = true
        
      } catch (err) {
        console.error('Camera initialization error:', err)
        
        if (err.name === 'NotAllowedError') {
          this.error = this.$t('camera.permission_denied')
        } else if (err.name === 'NotFoundError') {
          this.error = this.$t('camera.not_found')
        } else {
          this.error = this.$t('camera.camera_error')
        }
        
        this.$emit('camera-error', err)
        
      } finally {
        this.loading = false
      }
    },
    
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
      }
      this.cameraActive = false
    },
    
    async switchCamera() {
      this.currentFacingMode = this.currentFacingMode === 'environment' ? 'user' : 'environment'
      await this.initCamera()
    },
    
    capturePhoto() {
      if (!this.cameraActive || this.capturing) return
      
      this.capturing = true
      
      try {
        const video = this.$refs.videoElement
        const canvas = this.$refs.canvasElement
        const context = canvas.getContext('2d')
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        
        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        // Convert to blob
        canvas.toBlob((blob) => {
          if (blob) {
            // Create preview URL
            this.capturedPhoto = URL.createObjectURL(blob)
            
            // Stop camera
            this.stopCamera()
            
            // Store blob for later use
            this.photoBlob = blob
          }
        }, 'image/jpeg', 0.9)
        
      } catch (err) {
        console.error('Photo capture error:', err)
        this.error = this.$t('camera.camera_error')
      } finally {
        this.capturing = false
      }
    },
    
    retakePhoto() {
      // Clean up previous photo
      if (this.capturedPhoto) {
        URL.revokeObjectURL(this.capturedPhoto)
        this.capturedPhoto = null
      }
      this.photoBlob = null
      
      // Restart camera
      this.initCamera()
    },
    
    usePhoto() {
      if (this.photoBlob) {
        this.$emit('photo-captured', {
          blob: this.photoBlob,
          url: this.capturedPhoto
        })
      }
    },
    
    setupMobileGestures() {
      // Add touch gestures for mobile devices
      if ('ontouchstart' in window) {
        const videoElement = this.$refs.videoElement
        if (videoElement) {
          // Double tap to switch camera
          let lastTap = 0
          videoElement.addEventListener('touchend', (e) => {
            const currentTime = new Date().getTime()
            const tapLength = currentTime - lastTap
            if (tapLength < 500 && tapLength > 0) {
              e.preventDefault()
              if (this.hasMultipleCameras) {
                this.switchCamera()
              }
            }
            lastTap = currentTime
          })
          
          // Pinch to zoom (if supported)
          let initialDistance = 0
          videoElement.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
              initialDistance = this.getDistance(e.touches[0], e.touches[1])
            }
          })
          
          videoElement.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
              e.preventDefault()
              const currentDistance = this.getDistance(e.touches[0], e.touches[1])
              const scale = currentDistance / initialDistance
              // Apply zoom if camera supports it
              this.applyZoom(scale)
            }
          })
        }
      }
    },
    
    getDistance(touch1, touch2) {
      const dx = touch1.clientX - touch2.clientX
      const dy = touch1.clientY - touch2.clientY
      return Math.sqrt(dx * dx + dy * dy)
    },
    
    applyZoom(scale) {
      // Apply zoom to video stream if supported
      if (this.stream && this.stream.getVideoTracks().length > 0) {
        const track = this.stream.getVideoTracks()[0]
        const capabilities = track.getCapabilities()
        
        if (capabilities.zoom) {
          const settings = track.getSettings()
          const currentZoom = settings.zoom || 1
          const newZoom = Math.max(
            capabilities.zoom.min,
            Math.min(capabilities.zoom.max, currentZoom * scale)
          )
          
          track.applyConstraints({
            advanced: [{ zoom: newZoom }]
          }).catch(err => {
            console.warn('Zoom not supported:', err)
          })
        }
      }
    }
  }
}
</script>

<style scoped>
.camera-interface {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.camera-container {
  position: relative;
  width: 100%;
  max-width: 500px;
  aspect-ratio: 4/3;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.viewfinder {
  position: relative;
  width: 80%;
  height: 60%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}

.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #fff;
}

.corner.top-left {
  top: -3px;
  left: -3px;
  border-right: none;
  border-bottom: none;
}

.corner.top-right {
  top: -3px;
  right: -3px;
  border-left: none;
  border-bottom: none;
}

.corner.bottom-left {
  bottom: -3px;
  left: -3px;
  border-right: none;
  border-top: none;
}

.corner.bottom-right {
  bottom: -3px;
  right: -3px;
  border-left: none;
  border-top: none;
}

.camera-instructions {
  position: absolute;
  bottom: 20px;
  color: white;
  text-align: center;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.camera-error, .camera-loading {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: white;
  text-align: center;
  padding: 2rem;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  margin-bottom: 1rem;
  font-size: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.camera-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.capture-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.capture-btn:hover:not(:disabled) {
  background: #0056b3;
}

.capture-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.capture-icon {
  font-size: 20px;
}

.switch-camera-btn {
  width: 48px;
  height: 48px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
}

.photo-preview {
  width: 100%;
  max-width: 500px;
}

.photo-preview img {
  width: 100%;
  border-radius: 12px;
}

.preview-controls {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: center;
}

.retake-btn, .use-photo-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retake-btn {
  background: #6c757d;
  color: white;
}

.retake-btn:hover {
  background: #545b62;
}

.use-photo-btn {
  background: #28a745;
  color: white;
}

.use-photo-btn:hover {
  background: #1e7e34;
}

/* Mobile-responsive design */
@media (max-width: 768px) {
  .camera-interface {
    padding: 0.5rem;
    height: 100vh;
    justify-content: space-between;
  }
  
  .camera-container {
    aspect-ratio: 3/4;
    max-width: 100%;
    flex: 1;
    max-height: 70vh;
  }
  
  .camera-overlay {
    padding: 1rem;
  }
  
  .viewfinder {
    width: 90%;
    height: 70%;
  }
  
  .camera-instructions {
    bottom: 10px;
    font-size: 16px;
    padding: 12px 20px;
  }
  
  .camera-controls {
    flex-direction: row;
    justify-content: center;
    padding: 1rem 0;
    gap: 2rem;
  }
  
  .capture-btn {
    padding: 16px 32px;
    font-size: 18px;
    border-radius: 30px;
    min-width: 160px;
  }
  
  .capture-icon {
    font-size: 24px;
  }
  
  .switch-camera-btn {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }
  
  .preview-controls {
    flex-direction: row;
    justify-content: space-around;
    padding: 1rem 0;
  }
  
  .retake-btn, .use-photo-btn {
    padding: 14px 24px;
    font-size: 16px;
    min-width: 120px;
  }
  
  .camera-error, .camera-loading {
    padding: 3rem 2rem;
  }
  
  .error-icon {
    font-size: 4rem;
  }
  
  .error-message {
    font-size: 18px;
  }
  
  .retry-btn {
    padding: 12px 24px;
    font-size: 16px;
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  .capture-btn,
  .switch-camera-btn,
  .retake-btn,
  .use-photo-btn,
  .retry-btn {
    min-height: 44px;
    touch-action: manipulation;
  }
  
  .capture-btn:active {
    transform: scale(0.95);
    transition: transform 0.1s;
  }
  
  .switch-camera-btn:active {
    transform: scale(0.9);
    transition: transform 0.1s;
  }
}

/* Landscape orientation on mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .camera-interface {
    flex-direction: row;
    align-items: stretch;
  }
  
  .camera-container {
    flex: 1;
    aspect-ratio: 16/9;
    max-height: 100vh;
  }
  
  .camera-controls {
    flex-direction: column;
    justify-content: center;
    padding: 0 1rem;
    min-width: 120px;
  }
  
  .camera-instructions {
    left: 50%;
    transform: translateX(-50%);
    bottom: 20px;
  }
}
</style>