<template>
  <div class="admin-container">
    <div class="sidebar">
      <div class="logo">
        <h2>管理后台</h2>
      </div>
      <nav class="nav">
        <button @click="goTo('/admin')" class="nav-item active">📊 仪表盘</button>
        <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
        <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
        <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
        <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
      </nav>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
    
    <div class="main-content">
      <div class="header">
        <h1>仪表盘</h1>
        <span class="admin-name">{{ admin?.username }}</span>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon users-icon">👥</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.user_count || 0 }}</span>
            <span class="stat-label">用户总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon vocab-icon">📖</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.vocab_count || 0 }}</span>
            <span class="stat-label">词库总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon test-icon">📝</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.test_count || 0 }}</span>
            <span class="stat-label">测评次数</span>
          </div>
        </div>
      </div>
      
      <div class="level-distribution">
        <h3>词库分级分布</h3>
        <div class="level-bars">
          <div v-for="(count, level) in stats.level_distribution" :key="level" class="level-bar-item">
            <span class="level-name">{{ getLevelName(level) }}</span>
            <div class="bar-container">
              <div class="bar-fill" :style="{ width: getBarWidth(count) + '%' }" :class="`level-${level}`"></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
        </div>
      </div>
      
      <div class="recent-tests">
        <h3>最近测评记录</h3>
        <table>
          <thead>
            <tr>
              <th>用户ID</th>
              <th>难度级别</th>
              <th>正确率</th>
              <th>预估水平</th>
              <th>测评时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in stats.recent_tests" :key="record.id">
              <td>{{ record.user_id || '匿名' }}</td>
              <td><span class="level-badge" :class="`level-${record.level}`">{{ getLevelName(record.level) }}</span></td>
              <td>{{ Math.round(record.accuracy * 100) }}%</td>
              <td><span class="level-badge" :class="`level-${record.estimated_level}`">{{ getLevelName(record.estimated_level) }}</span></td>
              <td>{{ record.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminAPI } from '../../utils/api'

const router = useRouter()

const admin = ref(null)
const stats = ref({
  user_count: 0,
  vocab_count: 0,
  test_count: 0,
  level_distribution: {},
  recent_tests: []
})

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/admin/login')
    return
  }
  
  const stored = localStorage.getItem('admin')
  if (stored) {
    admin.value = JSON.parse(stored)
  }
  
  try {
    const response = await adminAPI.stats()
    if (response.data.success) {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('获取统计失败', error)
  }
})

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
}

const getBarWidth = (count) => {
  const maxCount = Math.max(...Object.values(stats.value.level_distribution), 1)
  return (count / maxCount) * 100
}

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('admin')
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  background: var(--bg-primary);
}

.sidebar {
  width: 250px;
  background: var(--bg-sidebar);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.logo h2 {
  color: var(--text-light);
  font-size: 20px;
  margin: 0 0 32px 0;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: var(--text-light);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-item.active {
  background: var(--accent-gradient);
}

.logout-btn {
  margin-top: auto;
  padding: 12px 16px;
  background: rgba(244, 67, 54, 0.2);
  border: none;
  border-radius: 8px;
  color: #ef9a9a;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(244, 67, 54, 0.3);
}

.main-content {
  flex: 1;
  padding: 32px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 28px;
  color: var(--text-primary);
}

.admin-name {
  color: var(--text-secondary);
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 28px;
}

.users-icon { background: var(--info-bg); }
.vocab-icon { background: var(--success-bg); }
.test-icon { background: #fff3e0; }

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
}

.level-distribution, .recent-tests {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}

.level-distribution h3, .recent-tests h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.level-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-bar-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.level-name {
  width: 60px;
  font-weight: 600;
  color: var(--text-secondary);
}

.bar-container {
  flex: 1;
  height: 24px;
  background: var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.5s;
}

.bar-fill.level-1 { background: linear-gradient(135deg, #4caf50 0%, #81c784 100%); }
.bar-fill.level-2 { background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%); }
.bar-fill.level-3 { background: linear-gradient(135deg, #f44336 0%, #ef9a9a 100%); }

.bar-value {
  width: 60px;
  text-align: right;
  font-weight: 600;
  color: var(--text-primary);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: var(--table-header-bg);
  font-weight: 600;
  color: var(--text-secondary);
}

.level-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.level-1 { background: var(--level-1-bg); color: var(--level-1-color); }
.level-2 { background: var(--level-2-bg); color: var(--level-2-color); }
.level-3 { background: var(--level-3-bg); color: var(--level-3-color); }
</style>