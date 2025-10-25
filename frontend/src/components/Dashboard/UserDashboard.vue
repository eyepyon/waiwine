<template>
  <div class="user-dashboard">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <div class="welcome-content">
        <div class="user-greeting">
          <h1 class="greeting-title">
            {{ $t('dashboard.welcome', { name: user?.name || $t('dashboard.guest') }) }}
          </h1>
          <p class="greeting-subtitle">{{ $t('dashboard.subtitle') }}</p>
        </div>
        
        <div class="user-stats">
          <div class="stat-card">
            <div class="stat-icon">🍷</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.winesRecognized }}</div>
              <div class="stat-label">{{ $t('dashboard.wines_recognized') }}</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">🎥</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.roomsJoined }}</div>
              <div class="stat-label">{{ $t('dashboard.rooms_joined') }}</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.connectionsMode }}</div>
              <div class="stat-label">{{ $t('dashboard.connections_made') }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Quick Actions -->
    <section class="quick-actions">
      <h2 class="section-title">{{ $t('dashboard.quick_actions') }}</h2>
      
      <div class="action-grid">
        <button @click="joinTestRoom" class="action-card primary action-button">
          <div class="action-icon">💬</div>
          <div class="action-content">
            <h3 class="action-title">{{ $t('room.join_test_room') }}</h3>
            <p class="action-description">{{ $t('room.test_room_description') }}</p>
          </div>
          <div class="action-arrow">→</div>
        </button>
        
        <router-link to="/camera" class="action-card">
          <div class="action-icon">📷</div>
          <div class="action-content">
            <h3 class="action-title">{{ $t('camera.capture_wine_label') }}</h3>
            <p class="action-description">{{ $t('camera.capture_description') }}</p>
          </div>
          <div class="action-arrow">→</div>
        </router-link>
        
        <router-link to="/rooms" class="action-card">
          <div class="action-icon">🎥</div>
          <div class="action-content">
            <h3 class="action-title">{{ $t('room.browse_rooms') }}</h3>
            <p class="action-description">{{ $t('room.browse_description') }}</p>
          </div>
          <div class="action-arrow">→</div>
        </router-link>
        
        <router-link to="/settings" class="action-card">
          <div class="action-icon">⚙️</div>
          <div class="action-content">
            <h3 class="action-title">{{ $t('settings.title') }}</h3>
            <p class="action-description">{{ $t('settings.description') }}</p>
          </div>
          <div class="action-arrow">→</div>
        </router-link>
      </div>
    </section>
    
    <!-- Recent Activity -->
    <section class="recent-activity">
      <h2 class="section-title">{{ $t('dashboard.recent_activity') }}</h2>
      
      <div v-if="recentActivity.length > 0" class="activity-list">
        <div
          v-for="activity in recentActivity"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon">{{ getActivityIcon(activity.type) }}</div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-description">{{ activity.description }}</div>
            <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
          </div>
          <button
            v-if="activity.actionable"
            @click="handleActivityAction(activity)"
            class="activity-action"
          >
            {{ $t('dashboard.view') }}
          </button>
        </div>
      </div>
      
      <div v-else class="empty-activity">
        <div class="empty-icon">📝</div>
        <p class="empty-text">{{ $t('dashboard.no_recent_activity') }}</p>
        <router-link to="/camera" class="empty-action">
          {{ $t('dashboard.start_exploring') }}
        </router-link>
      </div>
    </section>
    
    <!-- Active Rooms -->
    <section v-if="activeRooms.length > 0" class="active-rooms">
      <h2 class="section-title">{{ $t('dashboard.active_rooms') }}</h2>
      
      <div class="rooms-grid">
        <div
          v-for="room in activeRooms"
          :key="room.id"
          class="room-card"
        >
          <div class="room-wine">
            <img
              v-if="room.wine.image_url"
              :src="room.wine.image_url"
              :alt="room.wine.name"
              class="wine-image"
            />
            <div v-else class="wine-placeholder">🍷</div>
          </div>
          
          <div class="room-info">
            <h3 class="room-wine-name">{{ room.wine.name }}</h3>
            <p class="room-participants">
              {{ $t('room.participants_count', { count: room.participantCount }) }}
            </p>
          </div>
          
          <router-link
            :to="{ name: 'VideoRoom', params: { wineId: room.wine.id } }"
            class="room-join-btn"
          >
            {{ $t('room.join') }}
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

export default {
  name: 'UserDashboard',
  
  setup() {
    const authStore = useAuthStore()
    const { t } = useI18n()
    const router = useRouter()
    
    const userStats = ref({
      winesRecognized: 0,
      roomsJoined: 0,
      connectionsMode: 0
    })
    
    const recentActivity = ref([])
    const activeRooms = ref([])
    const loading = ref(true)
    
    const user = computed(() => authStore.user)
    
    const loadDashboardData = async () => {
      try {
        loading.value = true
        
        // Load user statistics with fallback data
        try {
          const statsResponse = await fetch('/api/user/stats', {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          })
          
          if (statsResponse.ok) {
            userStats.value = await statsResponse.json()
          }
        } catch (error) {
          console.warn('Failed to load user stats:', error)
          // Use default stats if API fails
          userStats.value = {
            winesRecognized: 0,
            roomsJoined: 0,
            connectionsMode: 0
          }
        }
        
        // Load recent activity with fallback
        try {
          const activityResponse = await fetch('/api/user/activity', {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          })
          
          if (activityResponse.ok) {
            recentActivity.value = await activityResponse.json()
          }
        } catch (error) {
          console.warn('Failed to load recent activity:', error)
          recentActivity.value = []
        }
        
        // Load active rooms with fallback
        try {
          const roomsResponse = await fetch('/api/rooms/active', {
            headers: {
              'Authorization': `Bearer ${authStore.token}`
            }
          })
          
          if (roomsResponse.ok) {
            activeRooms.value = await roomsResponse.json()
          }
        } catch (error) {
          console.warn('Failed to load active rooms:', error)
          activeRooms.value = []
        }
        
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        // Show error toast only for critical failures
        if (window.showToast) {
          window.showToast(t('dashboard.load_error'), 'error')
        }
      } finally {
        loading.value = false
      }
    }
    
    const getActivityIcon = (type) => {
      const icons = {
        wine_recognized: '🍷',
        room_joined: '🎥',
        connection_made: '👥',
        settings_updated: '⚙️'
      }
      return icons[type] || '📝'
    }
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diffInHours = (now - date) / (1000 * 60 * 60)
      
      if (diffInHours < 1) {
        return t('time.minutes_ago', { minutes: Math.floor(diffInHours * 60) })
      } else if (diffInHours < 24) {
        return t('time.hours_ago', { hours: Math.floor(diffInHours) })
      } else {
        return t('time.days_ago', { days: Math.floor(diffInHours / 24) })
      }
    }
    
    const handleActivityAction = (activity) => {
      // Handle different activity actions
      switch (activity.type) {
        case 'wine_recognized':
          // Navigate to wine details or room
          break
        case 'room_joined':
          // Navigate to room
          break
        default:
          console.log('Activity action:', activity)
      }
    }
    
    const joinTestRoom = async () => {
      try {
        // Create or join a test room without wine recognition
        const testWineId = 'test-room-001'
        
        // Navigate to video room with test wine ID
        router.push({
          name: 'VideoRoom',
          params: { wineId: testWineId },
          query: { test: 'true' }
        })
      } catch (error) {
        console.error('Failed to join test room:', error)
        if (window.showToast) {
          window.showToast(t('room.join_error'), 'error')
        }
      }
    }
    
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      user,
      userStats,
      recentActivity,
      activeRooms,
      loading,
      getActivityIcon,
      formatTime,
      handleActivityAction,
      joinTestRoom
    }
  }
}
</script>

<style scoped>
.user-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

/* Welcome Section */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.user-greeting {
  flex: 1;
}

.greeting-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.greeting-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.user-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  min-width: 100px;
  backdrop-filter: blur(10px);
}

.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

/* Section Titles */
.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
}

/* Quick Actions */
.quick-actions {
  margin-bottom: 3rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-button {
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.action-card.primary {
  border-color: #007bff;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
}

.action-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.action-description {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

.action-arrow {
  font-size: 1.2rem;
  opacity: 0.7;
  transition: transform 0.2s ease;
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
}

/* Recent Activity */
.recent-activity {
  margin-bottom: 3rem;
}

.activity-list {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-item:hover {
  background: #f8f9fa;
}

.activity-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.activity-description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.8rem;
  color: #999;
}

.activity-action {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.activity-action:hover {
  background: #0056b3;
}

/* Empty State */
.empty-activity {
  text-align: center;
  padding: 3rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  color: #666;
  margin-bottom: 1.5rem;
}

.empty-action {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.empty-action:hover {
  background: #0056b3;
}

/* Active Rooms */
.active-rooms {
  margin-bottom: 2rem;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.room-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.room-card:hover {
  transform: translateY(-2px);
}

.room-wine {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.wine-image {
  width: 60px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.wine-placeholder {
  width: 60px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 8px;
  font-size: 2rem;
}

.room-info {
  text-align: center;
  margin-bottom: 1rem;
}

.room-wine-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.room-participants {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.room-join-btn {
  display: block;
  width: 100%;
  background: #28a745;
  color: white;
  padding: 0.75rem;
  border-radius: 8px;
  text-align: center;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.room-join-btn:hover {
  background: #218838;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .greeting-title {
    font-size: 1.5rem;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    padding: 1rem;
  }
  
  .rooms-grid {
    grid-template-columns: 1fr;
  }
}
</style>
</template>