<template>
  <div class="test-start-container">
    <div class="card">
      <h2>选择测评模式</h2>
      
      <div class="mode-section">
        <h3>词库选择</h3>
        <div class="level-options">
          <label v-for="level in levels" :key="level.value" class="level-option">
            <input type="radio" v-model="selectedLevel" :value="level.value">
            <span class="level-label" :class="`level-${level.value}`">{{ level.label }}</span>
            <span class="level-desc">{{ level.desc }}</span>
          </label>
        </div>
      </div>

      <div class="mode-section">
        <h3>测评模式</h3>
        <div class="mode-options">
          <label class="mode-option">
            <input type="radio" v-model="testMode" value="basic">
            <span class="mode-icon">📝</span>
            <div>
              <span class="mode-title">基础测评</span>
              <span class="mode-desc">适合初次测评，随机出题</span>
            </div>
          </label>
          <label class="mode-option">
            <input type="radio" v-model="testMode" value="smart">
            <span class="mode-icon">🎯</span>
            <div>
              <span class="mode-title">智能测评</span>
              <span class="mode-desc">结合错题本，个性化出题</span>
            </div>
          </label>
          <label class="mode-option">
            <input type="radio" v-model="testMode" value="standard">
            <span class="mode-icon">📊</span>
            <div>
              <span class="mode-title">标准测评</span>
              <span class="mode-desc">50题标准测试，精准评估词汇量</span>
            </div>
          </label>
        </div>
        <p v-if="testMode === 'smart' && !isLoggedIn" class="warning">智能测评需要登录账号</p>
      </div>

      <div class="button-group">
        <button @click="goBack" class="btn-secondary">返回</button>
        <button @click="startTest" class="btn-primary" :disabled="loading">
  <span v-if="loading">加载中...</span>
  <span v-else>开始测评</span>
</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { testAPI } from '../utils/api'

const router = useRouter()

const levels = [
  { value: 1, label: '小学高频词汇', desc: '基础日常词汇' },
  { value: 2, label: '初中高频词汇', desc: '常用核心词汇' },
  { value: 3, label: '高中高频词汇', desc: '进阶提升词汇' }
]

const selectedLevel = ref(2)
const testMode = ref('basic')
const isLoggedIn = ref(false)
const loading = ref(false)

onMounted(() => {
  const storedLevel = localStorage.getItem('test_level')
  if (storedLevel) {
    selectedLevel.value = parseInt(storedLevel)
    localStorage.removeItem('test_level')
  }
  
  if (localStorage.getItem('access_token')) {
    isLoggedIn.value = true
  }
})

const goBack = () => {
  router.push('/')
}

const startTest = async () => {
  loading.value = true
  localStorage.setItem('test_level', selectedLevel.value)
  localStorage.setItem('test_mode', testMode.value)
  
  try {
    let response
    if (testMode.value === 'standard') {
      response = await testAPI.startStandard({})
    } else if (testMode.value === 'smart' && isLoggedIn.value) {
      response = await testAPI.startSmart({ level: selectedLevel.value })
    } else {
      response = await testAPI.start({ level: selectedLevel.value, mode: 'basic' })
    }
    
    if (response.data.success) {
      localStorage.setItem('questions', JSON.stringify(response.data.questions))
      router.push('/test')
    }
  } catch (error) {
    alert(error.response?.data?.message || '获取题目失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.test-start-container {
  min-height: 100vh;
  background: var(--bg-hero);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  max-width: 700px;
  width: 100%;
  background: var(--bg-card);
  border-radius: 24px;
  padding: 48px;
  box-shadow: var(--shadow-hover);
}

.card h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 40px;
  font-size: 32px;
  font-weight: 700;
}

.mode-section {
  margin-bottom: 40px;
}

.mode-section h3 {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-left: 8px;
  border-left: 4px solid var(--accent-primary);
}

.level-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.level-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  border: 3px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-primary);
}

.level-option:hover {
  border-color: var(--accent-primary);
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.level-option input {
  display: none;
}

.level-option:has(input:checked) {
  border-color: var(--accent-primary);
  background: var(--bg-primary);
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.level-label {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 10px;
}

.level-1 { 
  background: var(--level-1-bg); 
  color: var(--level-1-color); 
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
}
.level-2 { 
  background: var(--level-2-bg); 
  color: var(--level-2-color); 
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
}
.level-3 { 
  background: var(--level-3-bg); 
  color: var(--level-3-color); 
  box-shadow: 0 2px 8px rgba(233, 30, 99, 0.2);
}

.level-desc {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mode-option {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border: 3px solid var(--border-color);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-primary);
}

.mode-option:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.mode-option input {
  display: none;
}

.mode-option:has(input:checked) {
  border-color: var(--accent-primary);
  background: var(--bg-primary);
  transform: translateY(-2px);
}

.mode-icon {
  font-size: 40px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  border-radius: 16px;
  color: var(--text-light);
}

.mode-option:has(input:checked) .mode-icon {
  background: var(--accent-gradient);
}

.mode-content {
  flex: 1;
}

.mode-title {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 16px;
  margin-bottom: 4px;
}

.mode-desc {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
}

.warning {
  color: #f57c00;
  font-size: 14px;
  margin-top: 16px;
  padding: 12px 16px;
  background: #fff8e1;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning::before {
  content: "⚠️";
}

.button-group {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  padding: 16px 48px;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--btn-secondary-bg);
  color: var(--accent-primary);
  padding: 16px 48px;
  border: 2px solid var(--accent-primary);
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-secondary:hover {
  background: var(--border-color);
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .card {
    padding: 32px 24px;
  }
  
  .card h2 {
    font-size: 26px;
  }
  
  .level-options {
    grid-template-columns: 1fr;
  }
  
  .level-option {
    flex-direction: row;
    justify-content: space-between;
    gap: 12px;
  }
  
  .level-label {
    margin-bottom: 0;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .btn-primary, .btn-secondary {
    width: 100%;
  }
}
</style>