<template>
  <div class="admin-container">
    <div class="sidebar">
      <div class="logo">
        <h2>管理后台</h2>
      </div>
      <nav class="nav">
        <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
        <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
        <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
        <button @click="goTo('/admin/records')" class="nav-item active">📝 测评记录</button>
        <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
      </nav>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
    
    <div class="main-content">
      <div class="header">
        <h1>测评记录</h1>
      </div>
      
      <div class="records-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户ID</th>
              <th>测评难度</th>
              <th>总题数</th>
              <th>正确数</th>
              <th>正确率</th>
              <th>预估水平</th>
              <th>测评时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="record.id">
              <td>{{ record.id }}</td>
              <td>{{ record.user_id || '匿名' }}</td>
              <td><span class="level-badge" :class="`level-${record.level}`">{{ getLevelName(record.level) }}</span></td>
              <td>{{ record.total_count }}</td>
              <td>{{ record.correct_count }}</td>
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

const records = ref([])

onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/admin/login')
    return
  }
  loadRecords()
})

const loadRecords = async () => {
  try {
    const response = await adminAPI.stats()
    if (response.data.success) {
      records.value = response.data.stats.recent_tests
    }
  } catch (error) {
    console.error('获取记录失败', error)
  }
}

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
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
  margin-bottom: 32px;
}

.header h1 {
  font-size: 28px;
  color: var(--text-primary);
}

.records-table {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
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