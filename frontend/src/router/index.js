/**
 * Vue Router configuration
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy load components
const Home = () => import('@/views/Home.vue')
const Landing = () => import('@/views/Landing.vue')
const Login = () => import('@/views/Login.vue')
const Camera = () => import('@/views/Camera.vue')
const VideoRoom = () => import('@/views/VideoRoom.vue')
const Settings = () => import('@/views/Settings.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/landing',
    name: 'Landing',
    component: Landing,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/camera',
    name: 'Camera',
    component: Camera,
    meta: { requiresAuth: true }
  },
  {
    path: '/room/:wineId',
    name: 'VideoRoom',
    component: VideoRoom,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/translation',
    name: 'TranslationSettings',
    component: () => import('@/views/TranslationSettings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/oauth/callback/:provider',
    name: 'OAuthCallback',
    component: () => import('@/views/OAuthCallback.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to landing page if authentication is required
    next({ name: 'Landing' })
  } else if ((to.name === 'Login' || to.name === 'Landing') && authStore.isAuthenticated) {
    // Redirect to home if already authenticated
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router