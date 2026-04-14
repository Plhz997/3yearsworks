<template>
  <div class="app-container">
    <router-view v-if="currentPage !== 'admin'"></router-view>
    <AdminLayout v-else-if="currentPage.startsWith('admin')"></AdminLayout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ElementPlus from 'element-plus'
import router from './router'

const currentPage = ref('home')

onMounted(() => {
  const path = window.location.pathname
  if (path.startsWith('/admin')) {
    currentPage.value = 'admin'
  } else {
    currentPage.value = path.replace('/', '') || 'home'
  }
})
</script>