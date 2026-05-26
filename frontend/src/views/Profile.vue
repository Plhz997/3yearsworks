<template>
  <div class="profile-container">
    <div class="header">
      <h2>个人中心</h2>
      <button @click="goBack" class="btn-back">← 返回</button>
    </div>
    
    <div class="profile-card">
      <div class="user-info">
        <div class="avatar">👤</div>
        <div class="user-details">
          <h3>{{ user?.username }}</h3>
          <p>{{ user?.email || '暂无邮箱' }}</p>
          <p class="join-date">注册于 {{ user?.created_at }}</p>
        </div>
      </div>
    </div>
    
    <div class="stats-card">
      <h3>学习统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_tests || 0 }}</span>
            <span class="stat-label">测评次数</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <span class="stat-value">{{ Math.round((stats.avg_accuracy || 0) * 100) }}%</span>
            <span class="stat-label">平均正确率</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.last_test_date || '-' }}</span>
            <span class="stat-label">上次测评</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="menu-card">
      <h3>功能菜单</h3>
      <div class="menu-items">
        <button @click="goTo('/history')" class="menu-item">
          <span class="menu-icon">📋</span>
          <span>测评历史</span>
          <span class="menu-arrow">→</span>
        </button>
        <button @click="goTo('/wrong-words')" class="menu-item">
          <span class="menu-icon">📖</span>
          <span>错题本</span>
          <span class="menu-arrow">→</span>
        </button>
        <button @click="goTo('/test/start')" class="menu-item">
          <span class="menu-icon">🎯</span>
          <span>开始测评</span>
          <span class="menu-arrow">→</span>
        </button>
      </div>
    </div>
    
    <div class="action-card">
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI, userAPI } from '../utils/api'

const router = useRouter()

const user = ref(null)
const stats = ref({
  total_tests: 0,
  avg_accuracy: 0,
  last_test_date: null
})

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/login')
    return
  }
  
  try {
    const [userRes, statsRes] = await Promise.all([
      authAPI.profile(),
      userAPI.stats()
    ])
    
    if (userRes.data.success) {
      user.value = userRes.data.user
    }
    
    if (statsRes.data.success) {
      stats.value = statsRes.data.stats
    }
  } catch (error) {
    console.error('获取数据失败', error)
  }
})

const goBack = () => {
  router.push('/')
}

const goTo = (path) => {
  console.log('Navigating to:', path)
  router.push(path)
}

const logout = () => {
  if (!confirm('确定要退出登录吗？')) return
  
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 40px 20px;
}

.header {
  max-width: 600px;
  margin: 0 auto 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  font-size: 28px;
  color: var(--text-primary);
}

.btn-back {
  padding: 10px 20px;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 14px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: var(--btn-secondary-bg);
}

.profile-card, .stats-card, .menu-card, .action-card {
  max-width: 600px;
  margin: 0 auto 20px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  background: var(--accent-gradient);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
}

.user-details h3 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.user-details p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 4px 0;
}

.join-date {
  color: var(--text-secondary) !important;
  font-size: 12px !important;
  opacity: 0.7;
}

.stats-card h3, .menu-card h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-primary);
}

.menu-item:hover {
  background: var(--border-color);
}

.menu-icon {
  font-size: 20px;
}

.menu-item span:nth-child(2) {
  flex: 1;
  text-align: left;
  padding-left: 16px;
  color: var(--text-primary);
  font-size: 16px;
}

.menu-arrow {
  color: var(--text-secondary);
}

.action-card {
  text-align: center;
}

.logout-btn {
  width: 100%;
  padding: 14px;
  background: var(--danger-bg);
  color: var(--danger-color);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: #ffcdd2;
}
</style>