<template>
  <MainLayout>
    <div class="camera-content">
      <WineRecognitionFlow />
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '@/components/Layout/MainLayout.vue'
import WineRecognitionFlow from '@/components/Wine/WineRecognitionFlow.vue'

export default {
  name: 'CameraView',
  components: {
    MainLayout,
    WineRecognitionFlow
  }
}
</script>

<style scoped>
.camera-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
</style>