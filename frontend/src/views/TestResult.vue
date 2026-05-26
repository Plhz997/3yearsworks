<template>
  <div class="result-container">
    <div class="result-card">
      <div class="result-header">
        <div class="score-circle">
          <div class="score">{{ Math.round(result.analysis.overall.accuracy * 100) }}</div>
          <div class="score-label">正确率</div>
        </div>
        <div class="vocab-estimate">
          <div class="vocab-count">{{ (result.vocab_size || estimatedVocab).toLocaleString() }}</div>
          <div class="vocab-label">预估词汇量</div>
          <div class="vocab-range">
            {{ result.vocab_range ? '约 ' + (result.vocab_range.low || 0).toLocaleString() + ' - ' + (result.vocab_range.high || 0).toLocaleString() + ' 词' : '' }}
          </div>
        </div>
      </div>
      
      <div class="result-info">
        <div class="info-row">
          <span class="info-label">测评结果</span>
          <span class="info-value level-badge" :class="`level-${result.estimated_level}`">{{ result.level_name }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">知识深度</span>
          <span class="info-value depth-tag" :class="depthClass">{{ result.analysis.knowledge_depth?.level || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">正确 / 总题</span>
          <span class="info-value">{{ result.analysis.overall.correct }} / {{ result.analysis.overall.total }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">加权得分</span>
          <span class="info-value correct">{{ (result.analysis.overall.weighted_accuracy * 100).toFixed(1) }}%</span>
        </div>
      </div>
      
      <!-- 各学段表现 -->
      <div class="level-analysis">
        <h3>各学段表现</h3>
        <div class="level-bars">
          <div v-for="(stats, level) in result.analysis.level_analysis" :key="level" class="level-bar-item">
            <span class="level-name">{{ level }}</span>
            <div class="bar-container">
              <div class="bar-fill" :style="{ width: (stats.accuracy * 100) + '%', background: getLevelColor(stats.accuracy) }"></div>
            </div>
            <span class="bar-value">{{ Math.round(stats.accuracy * 100) }}%</span>
            <span class="bar-detail">{{ stats.correct }}/{{ stats.total }}</span>
          </div>
        </div>
      </div>
      
      <!-- 新增：题型分析 -->
      <div v-if="result.analysis.type_analysis && Object.keys(result.analysis.type_analysis).length > 0" class="type-analysis">
        <h3>题型表现</h3>
        <div class="type-grid">
          <div v-for="(stats, typeName) in result.analysis.type_analysis" :key="typeName" class="type-card">
            <div class="type-header">
              <span class="type-name">{{ typeName }}</span>
              <span class="type-weight" :title="'权重: ' + stats.weight">⚖️ {{ stats.weight }}</span>
            </div>
            <div class="type-bar-bg">
              <div class="type-bar-fill" :style="{ width: (stats.accuracy * 100) + '%' }"></div>
            </div>
            <div class="type-stats">
              <span>{{ stats.correct }}/{{ stats.total }}</span>
              <span>{{ Math.round(stats.accuracy * 100) }}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="suggestions">
        <h3>学习建议</h3>
        <ul>
          <li v-for="(suggestion, index) in displaySuggestions" :key="index">{{ suggestion }}</li>
        </ul>
      </div>
      
      <div class="button-group">
        <button @click="goHome" class="btn-secondary">返回首页</button>
        <button @click="retest" class="btn-primary">再次测评</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const result = ref({
  analysis: {
    overall: { total: 0, correct: 0, accuracy: 0, weighted_accuracy: 0 },
    level_analysis: {},
    type_analysis: {},
    knowledge_depth: { score: 0, level: '-' },
    suggestions: []
  },
  estimated_level: 2,
  level_name: '',
  vocab_size: 0,
  vocab_range: null
})

// 仅在旧数据（后端未返回vocab_size）时使用
const estimatedVocab = computed(() => {
  const analysis = result.value.analysis
  const level = result.value.estimated_level
  const levelVocabRanges = {
    1: { min: 200, max: 800, base: 500 },
    2: { min: 800, max: 2000, base: 1400 },
    3: { min: 2000, max: 4500, base: 3200 }
  }
  const range = levelVocabRanges[level] || levelVocabRanges[2]
  const accuracy = analysis.overall.accuracy
  return Math.round(range.min + (range.max - range.min) * accuracy)
})

// 使用后端建议优先
const displaySuggestions = computed(() => {
  return result.value.analysis.suggestions?.length > 0
    ? result.value.analysis.suggestions
    : ['继续保持，你的词汇学习策略很有效！']
})

// 知识深度对应的样式类
const depthClass = computed(() => {
  const level = result.value.analysis.knowledge_depth?.level || ''
  if (level === '深度掌握') return 'depth-master'
  if (level === '良好掌握') return 'depth-good'
  if (level === '基础掌握') return 'depth-basic'
  return 'depth-weak'
})

onMounted(() => {
  const stored = localStorage.getItem('test_result')
  if (stored) {
    result.value = JSON.parse(stored)
  } else {
    router.push('/test/start')
  }
})

const getLevelColor = (accuracy) => {
  if (accuracy >= 0.8) return 'linear-gradient(135deg, #4caf50 0%, #81c784 100%)'
  if (accuracy >= 0.6) return 'linear-gradient(135deg, #ffb74d 0%, #ff9800 100%)'
  return 'linear-gradient(135deg, #f44336 0%, #ef9a9a 100%)'
}

const goHome = () => {
  localStorage.removeItem('test_result')
  router.push('/')
}

const retest = () => {
  localStorage.removeItem('test_result')
  router.push('/test/start')
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: var(--bg-hero);
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.result-card {
  max-width: 600px;
  width: 100%;
  background: var(--bg-card);
  border-radius: 20px;
  padding: 40px;
  box-shadow: var(--shadow-hover);
}

.result-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  margin-bottom: 32px;
}

.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  background: var(--accent-gradient);
  border-radius: 50%;
  color: var(--text-light);
}

.score {
  font-size: 48px;
  font-weight: 700;
}

.score-label {
  font-size: 14px;
  opacity: 0.9;
}

.vocab-estimate {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  background: linear-gradient(135deg, #4caf50 0%, #81c784 100%);
  border-radius: 50%;
  color: white;
}

.vocab-count {
  font-size: 40px;
  font-weight: 700;
}

.vocab-label {
  font-size: 14px;
  opacity: 0.9;
}

.vocab-range {
  font-size: 10px;
  opacity: 0.85;
  margin-top: 4px;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 10px;
}

.result-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 12px;
}

.info-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  font-size: 18px;
  color: var(--text-primary);
}

.info-value.correct {
  color: var(--success-color);
}

.info-value.wrong {
  color: var(--danger-color);
}

.level-badge {
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.level-1 { background: var(--level-1-bg); color: var(--level-1-color); }
.level-2 { background: var(--level-2-bg); color: var(--level-2-color); }
.level-3 { background: var(--level-3-bg); color: var(--level-3-color); }

.level-analysis {
  margin-bottom: 32px;
}

.level-analysis h3 {
  color: var(--text-primary);
  font-size: 18px;
  margin-bottom: 16px;
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

.bar-value {
  width: 60px;
  text-align: right;
  font-weight: 600;
  color: var(--text-primary);
}

.bar-detail {
  width: 45px;
  text-align: right;
  font-size: 12px;
  color: var(--text-secondary);
}

/* ===== 题型分析 ===== */
.type-analysis {
  margin-bottom: 24px;
}

.type-analysis h3 {
  color: var(--text-primary);
  font-size: 18px;
  margin-bottom: 16px;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.type-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 16px;
}

.type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.type-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.type-weight {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-card);
  padding: 2px 8px;
  border-radius: 10px;
}

.type-bar-bg {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.type-bar-fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 4px;
  transition: width 0.5s;
}

.type-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}

/* ===== 知识深度 ===== */
.depth-tag {
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 13px;
}

.depth-master { background: #e8f5e9; color: #2e7d32; }
.depth-good { background: #e3f2fd; color: #1565c0; }
.depth-basic { background: #fff3e0; color: #e65100; }
.depth-weak { background: #ffebee; color: #c62828; }

.suggestions {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--info-bg);
  border-radius: 12px;
}

.suggestions h3 {
  color: var(--info-color);
  font-size: 16px;
  margin-bottom: 12px;
}

.suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions li {
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.button-group {
  display: flex;
  gap: 16px;
}

.btn-primary {
  flex: 1;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  padding: 14px;
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

.btn-secondary {
  flex: 1;
  background: var(--btn-secondary-bg);
  color: var(--text-secondary);
  padding: 14px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: var(--border-color);
}
</style>