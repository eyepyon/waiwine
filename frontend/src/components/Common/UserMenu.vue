<template>
  <div class="user-menu">
    <button 
      @click="toggleDropdown"
      class="user-btn"
      :class="{ active: showDropdown }"
    >
      <img 
        v-if="user?.profile_image_url"
        :src="user.profile_image_url"
        :alt="user.name"
        class="user-avatar"
      />
      <div v-else class="user-avatar-placeholder">
        {{ userInitials }}
      </div>
      <span class="user-name">{{ user?.name }}</span>
      <span class="dropdown-arrow">▼</span>
    </button>
    
    <div v-if="showDropdown" class="user-dropdown">
      <div class="user-info">
        <div class="user-details">
          <div class="user-display-name">{{ user?.name }}</div>
          <div class="user-email">{{ user?.email }}</div>
        </div>
      </div>
      
      <div class="dropdown-divider"></div>
      
      <router-link to="/settings" class="dropdown-item" @click="closeDropdown">
        <span class="item-icon">⚙️</span>
        {{ $t('settings.title') }}
      </router-link>
      
      <button @click="handleLogout" class="dropdown-item logout-item">
        <span class="item-icon">🚪</span>
        {{ $t('auth.logout') }}
      </button>
    </div>
    
    <!-- Backdrop to close dropdown -->
    <div 
      v-if="showDropdown" 
      class="dropdown-backdrop"
      @click="closeDropdown"
    ></div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'UserMenu',
  
  data() {
    return {
      showDropdown: false
    }
  },
  
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    return {
      authStore,
      router
    }
  },
  
  computed: {
    user() {
      return this.authStore.user
    },
    
    userInitials() {
      if (!this.user?.name) return '?'
      
      return this.user.name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2)
    }
  },
  
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown
    },
    
    closeDropdown() {
      this.showDropdown = false
    },
    
    async handleLogout() {
      this.closeDropdown()
      
      const success = await this.authStore.logout()
      
      if (success) {
        this.router.push({ name: 'Login' })
      }
    }
  },
  
  mounted() {
    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
      if (!this.$el.contains(event.target)) {
        this.closeDropdown()
      }
    })
  }
}
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-btn:hover,
.user-btn.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.user-name {
  font-weight: 500;
  font-size: 0.9rem;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.2s ease;
}

.user-btn.active .dropdown-arrow {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 200px;
}

.user-info {
  padding: 1rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-display-name {
  font-weight: 600;
  color: #333;
}

.user-email {
  font-size: 0.8rem;
  color: #666;
}

.dropdown-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  text-align: left;
  text-decoration: none;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.logout-item {
  color: #dc3545;
}

.logout-item:hover {
  background: #fff5f5;
}

.item-icon {
  font-size: 1rem;
}

.dropdown-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

@media (max-width: 768px) {
  .user-name {
    display: none;
  }
  
  .user-dropdown {
    right: -1rem;
  }
}
</style>