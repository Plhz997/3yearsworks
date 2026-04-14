const { createApp } = Vue

const app = createApp({
  template: `
    <div class="app-container">
      <router-view v-if="currentPage !== 'admin'"></router-view>
      <AdminLayout v-else-if="currentPage.startsWith('admin')"></AdminLayout>
    </div>
  `,
  data() {
    return {
      currentPage: 'home'
    }
  },
  mounted() {
    const path = window.location.pathname
    if (path.startsWith('/admin')) {
      this.currentPage = 'admin'
    } else {
      this.currentPage = path.replace('/', '') || 'home'
    }
  }
})

app.use(ElementPlus)
app.mount('#app')