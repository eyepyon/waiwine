<template>
  <MainLayout>
    <UserDashboard />
  </MainLayout>
</template>

<script>
import MainLayout from '@/components/Layout/MainLayout.vue'
import UserDashboard from '@/components/Dashboard/UserDashboard.vue'

export default {
  name: 'HomeView',
  
  components: {
    MainLayout,
    UserDashboard
  }
}
</script>

<style scoped>
/* Home view now uses MainLayout and UserDashboard components */
</style>