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
        <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
        <button @click="goTo('/admin/stats')" class="nav-item active">📈 数据统计</button>
      </nav>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
    
    <div class="main-content">
      <div class="header">
        <h1>数据统计</h1>
      </div>
      
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-value">{{ stats.user_count || 0 }}</div>
          <div class="stat-label">用户总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.vocab_count || 0 }}</div>
          <div class="stat-label">单词总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.test_count || 0 }}</div>
          <div class="stat-label">测评次数</div>
        </div>
      </div>
      
      <div class="chart-section">
        <h3>词库分级统计</h3>
        <div id="levelChart" style="height: 300px;"></div>
      </div>
      
      <div class="chart-section">
        <h3>测评等级分布</h3>
        <div id="levelDistChart" style="height: 300px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { adminAPI } from '../../utils/api'

const router = useRouter()

const stats = ref({
  user_count: 0,
  vocab_count: 0,
  test_count: 0,
  level_distribution: {}
})

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/admin/login')
    return
  }
  
  try {
    const response = await adminAPI.stats()
    if (response.data.success) {
      stats.value = response.data.stats
      await nextTick()
      initCharts()
    }
  } catch (error) {
    console.error('获取统计失败', error)
  }
})

const initCharts = () => {
  const levelChart = echarts.init(document.getElementById('levelChart'))
  const levelDistChart = echarts.init(document.getElementById('levelDistChart'))
  
  const levelData = [
    { value: stats.value.level_distribution[1] || 0, name: '小学' },
    { value: stats.value.level_distribution[2] || 0, name: '初中' },
    { value: stats.value.level_distribution[3] || 0, name: '高中' }
  ]
  
  levelChart.setOption({
    title: { text: '词库分级' },
    tooltip: { trigger: 'item' },
    legend: { orient: 'horizontal', bottom: 10 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10 },
      label: { show: true },
      data: levelData
    }]
  })
  
  const levelCounts = { 1: 0, 2: 0, 3: 0 }
  if (stats.value.recent_tests) {
    stats.value.recent_tests.forEach(record => {
      levelCounts[record.estimated_level] = (levelCounts[record.estimated_level] || 0) + 1
    })
  }
  
  levelDistChart.setOption({
    title: { text: '预估水平分布' },
    tooltip: {},
    xAxis: { data: ['小学', '初中', '高中'] },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: [levelCounts[1], levelCounts[2], levelCounts[3]],
      itemStyle: {
        color: ['#4caf50', '#ff9800', '#f44336']
      }
    }]
  })
  
  window.addEventListener('resize', () => {
    levelChart.resize()
    levelDistChart.resize()
  })
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
  background: #f5f7fa;
}

.sidebar {
  width: 250px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.logo h2 {
  color: white;
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
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: #333;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.chart-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}
</style>