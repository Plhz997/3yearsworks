<template>
  <div class="result-container">
    <div class="result-card">
      <div class="result-header">
        <div class="score-circle">
          <div class="score">{{ Math.round(result.analysis.overall.accuracy * 100) }}</div>
          <div class="score-label">正确率</div>
        </div>
        <div class="vocab-estimate">
          <div class="vocab-count">{{ estimatedVocabulary }}</div>
          <div class="vocab-label">预估词汇量</div>
          <div class="vocab-range">约 {{ vocabularyRange.low }} - {{ vocabularyRange.high }} 词</div>
        </div>
      </div>
      
      <div class="result-info">
        <div class="info-row">
          <span class="info-label">测评结果</span>
          <span class="info-value level-badge" :class="`level-${result.estimated_level}`">{{ result.level_name }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">总题数</span>
          <span class="info-value">{{ result.analysis.overall.total }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">正确数</span>
          <span class="info-value correct">{{ result.analysis.overall.correct }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">错误数</span>
          <span class="info-value wrong">{{ result.analysis.overall.total - result.analysis.overall.correct }}</span>
        </div>
      </div>
      
      <div class="level-analysis">
        <h3>各学段表现</h3>
        <div class="level-bars">
          <div v-for="(stats, level) in result.analysis.level_analysis" :key="level" class="level-bar-item">
            <span class="level-name">{{ level }}</span>
            <div class="bar-container">
              <div class="bar-fill" :style="{ width: (stats.accuracy * 100) + '%', background: getLevelColor(stats.accuracy) }"></div>
            </div>
            <span class="bar-value">{{ Math.round(stats.accuracy * 100) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="suggestions">
        <h3>学习建议</h3>
        <ul>
          <li v-for="(suggestion, index) in suggestions" :key="index">{{ suggestion }}</li>
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
    overall: { total: 0, correct: 0, accuracy: 0 },
    level_analysis: {}
  },
  estimated_level: 2,
  level_name: ''
})

const estimatedVocabulary = computed(() => {
  const analysis = result.value.analysis
  const level = result.value.estimated_level
  
  const levelVocabRanges = {
    1: { min: 600, max: 1200, base: 800 },
    2: { min: 1500, max: 3000, base: 2000 },
    3: { min: 3000, max: 5000, base: 3500 }
  }
  
  const range = levelVocabRanges[level] || levelVocabRanges[2]
  const accuracy = analysis.overall.accuracy
  
  const vocabRange = range.max - range.min
  const estimated = Math.round(range.min + vocabRange * accuracy)
  
  return Math.max(range.min * 0.5, Math.min(range.max * 1.2, estimated)).toLocaleString()
})

const vocabularyRange = computed(() => {
  const level = result.value.estimated_level
  
  const levelRanges = {
    1: { min: 400, max: 1500 },
    2: { min: 1200, max: 3500 },
    3: { min: 2500, max: 5500 }
  }
  
  const range = levelRanges[level] || levelRanges[2]
  const vocab = parseInt(estimatedVocabulary.value.replace(/,/g, ''))
  
  const margin = Math.round(vocab * 0.1)
  
  return {
    low: Math.max(range.min, vocab - margin).toLocaleString(),
    high: Math.min(range.max, vocab + margin).toLocaleString()
  }
})

const suggestions = computed(() => {
  const acc = result.value.analysis.overall.accuracy
  const level = result.value.estimated_level
  const suggestions = []
  
  if (acc >= 0.9) {
    suggestions.push('🎉 表现优秀！继续保持，可以挑战更高难度')
    if (level < 3) {
      suggestions.push(`建议尝试${level === 1 ? '初中' : '高中'}词汇测评`)
    }
  } else if (acc >= 0.7) {
    suggestions.push('👍 表现良好，还有提升空间')
    suggestions.push('建议复习错题本中的单词')
  } else if (acc >= 0.5) {
    suggestions.push('💪 需要加强练习，多背单词')
    suggestions.push('建议从较低难度开始练习')
  } else {
    suggestions.push('📚 需要系统学习基础词汇')
    suggestions.push('建议每天坚持背单词')
  }
  
  return suggestions
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.result-card {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  color: white;
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
  background: #f8f9fa;
  border-radius: 12px;
}

.info-label {
  color: #666;
  font-size: 14px;
}

.info-value {
  font-weight: 600;
  font-size: 18px;
  color: #333;
}

.info-value.correct {
  color: #4caf50;
}

.info-value.wrong {
  color: #f44336;
}

.level-badge {
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.level-1 { background: #e8f5e9; color: #2e7d32; }
.level-2 { background: #fff3e0; color: #e65100; }
.level-3 { background: #fce4ec; color: #c2185b; }

.level-analysis {
  margin-bottom: 32px;
}

.level-analysis h3 {
  color: #333;
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
  color: #666;
}

.bar-container {
  flex: 1;
  height: 24px;
  background: #e4e7ed;
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
  color: #333;
}

.suggestions {
  margin-bottom: 32px;
  padding: 20px;
  background: #fff3e0;
  border-radius: 12px;
}

.suggestions h3 {
  color: #e65100;
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
  color: #666;
  font-size: 14px;
}

.button-group {
  display: flex;
  gap: 16px;
}

.btn-primary {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
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
  background: #f5f7fa;
  color: #666;
  padding: 14px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #e4e7ed;
}
</style>