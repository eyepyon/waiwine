<template>
  <div class="video-room-view">
    <VideoRoom :wine-id="wineId" />
  </div>
</template>

<script>
import VideoRoom from '@/components/VideoChat/VideoRoom.vue'

export default {
  name: 'VideoRoomView',
  components: {
    VideoRoom
  },
  props: {
    wineId: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.video-room-view {
  height: 100vh;
  overflow: hidden;
}
</style>