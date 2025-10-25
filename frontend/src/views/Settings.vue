<template>
  <MainLayout>
    <div class="settings-view">
      <UserSettings />
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '@/components/Layout/MainLayout.vue'
import UserSettings from '@/components/User/UserSettings.vue'

export default {
  name: 'Settings',
  components: {
    MainLayout,
    UserSettings
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: #f5f5f5;
}