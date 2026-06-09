<template>
  <div class="history-container">
    <div class="header">
      <h2>测评历史记录</h2>
      <button @click="goBack" class="btn-back">← 返回</button>
    </div>
    
    <div v-if="records.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p>暂无测评记录</p>
      <button @click="goTest" class="btn-primary">开始测评</button>
    </div>
    
    <div v-else class="records-list">
      <div v-for="record in records" :key="record.id" class="record-card">
        <div class="record-header">
          <span class="level-badge" :class="`level-${record.level}`">{{ getLevelName(record.level) }}</span>
          <span class="date">{{ record.created_at }}</span>
        </div>
        <div class="record-stats">
          <div class="stat-item">
            <span class="stat-value">{{ Math.round(record.accuracy * 100) }}%</span>
            <span class="stat-label">正确率</span>
          </div>
          <div class="stat-item">
            <span class="stat-value correct">{{ record.correct_count }}/{{ record.total_count }}</span>
            <span class="stat-label">正确数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value level-badge" :class="`level-${record.estimated_level}`">{{ getLevelName(record.estimated_level) }}</span>
            <span class="stat-label">预估水平</span>
          </div>
        </div>
        <div class="record-footer">
          <button @click="viewDetail(record.id)" class="btn-detail">查看详情</button>
        </div>
      </div>
    </div>
    
    <div v-if="showDetail" class="detail-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>测评详情</h3>
          <button @click="closeDetail" class="close-btn">×</button>
        </div>
        <div v-if="detailData" class="modal-body">
          <div class="detail-summary">
            <div class="summary-item">
              <span class="summary-label">正确率</span>
              <span class="summary-value">{{ Math.round(detailData.record.accuracy * 100) }}%</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">预估水平</span>
              <span class="summary-value level-badge" :class="`level-${detailData.record.estimated_level}`">{{ getLevelName(detailData.record.estimated_level) }}</span>
            </div>
          </div>
          <div class="detail-questions">
            <h4>答题详情</h4>
            <div v-for="(detail, index) in detailData.details" :key="detail.id" class="question-detail">
              <div class="question-header">
                <span class="question-num">第{{ index + 1 }}题</span>
                <span :class="detail.is_correct ? 'correct-tag' : 'wrong-tag'">{{ detail.is_correct ? '正确' : '错误' }}</span>
              </div>
              <p><strong>{{ detail.word }}</strong> - {{ detail.meaning }}</p>
              <p v-if="!detail.is_correct" class="user-answer">你的答案: {{ detail.user_answer || '未作答' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { testAPI } from '../utils/api'

const router = useRouter()

const records = ref([])
const showDetail = ref(false)
const detailData = ref(null)

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/login')
    return
  }
  
  try {
    const response = await testAPI.records()
    if (response.data.success) {
      records.value = response.data.records
    }
  } catch (error) {
    console.error('获取记录失败', error)
  }
})

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
}

const goBack = () => {
  router.push('/')
}

const goTest = () => {
  router.push('/test/start')
}

const viewDetail = async (id) => {
  try {
    const response = await testAPI.record(id)
    if (response.data.success) {
      detailData.value = response.data
      showDetail.value = true
    }
  } catch (error) {
    console.error('获取详情失败', error)
  }
}

const closeDetail = () => {
  showDetail.value = false
  detailData.value = null
}
</script>

<style scoped>
.history-container {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 40px 20px;
}

.header {
  max-width: 800px;
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

.empty-state {
  max-width: 400px;
  margin: 0 auto;
  text-align: center;
  padding: 60px 40px;
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 24px;
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.records-list {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.record-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.record-header .date {
  color: var(--text-secondary);
  font-size: 14px;
}

.record-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.correct {
  color: var(--success-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.record-footer {
  text-align: right;
}

.btn-detail {
  padding: 8px 20px;
  background: var(--btn-secondary-bg);
  border: none;
  border-radius: 6px;
  color: var(--accent-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-detail:hover {
  background: var(--border-color);
}

.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.modal-content {
  background: var(--bg-card);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 20px;
  color: var(--text-primary);
}

.close-btn {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
}

.modal-body {
  padding: 24px;
}

.detail-summary {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-questions h4 {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.question-detail {
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 8px;
  margin-bottom: 12px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.question-num {
  font-size: 12px;
  color: var(--text-secondary);
}

.correct-tag {
  color: var(--success-color);
  font-size: 12px;
  font-weight: 600;
}

.wrong-tag {
  color: var(--danger-color);
  font-size: 12px;
  font-weight: 600;
}

.user-answer {
  color: var(--danger-color);
  font-size: 14px;
  margin-top: 8px;
}
</style>