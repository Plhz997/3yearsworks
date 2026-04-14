<template>
  <div class="wrong-words-container">
    <div class="header">
      <h2>错题本</h2>
      <button @click="goBack" class="btn-back">← 返回</button>
    </div>
    
    <div v-if="wrongWords.length === 0" class="empty-state">
      <div class="empty-icon">✅</div>
      <p>太棒了！暂无错题</p>
    </div>
    
    <div v-else class="words-list">
      <div v-for="word in wrongWords" :key="word.id" class="word-card">
        <div class="word-info">
          <div class="word-header">
            <h3>{{ word.word }}</h3>
            <span class="level-badge" :class="`level-${word.level}`">{{ getLevelName(word.level) }}</span>
          </div>
          <p class="meaning">{{ word.meaning }}</p>
          <p v-if="word.phonetic" class="phonetic">{{ word.phonetic }}</p>
          <p v-if="word.example" class="example">{{ word.example }}</p>
          <div class="wrong-info">
            <span class="wrong-count">错误次数: {{ word.wrong_count }}</span>
            <span v-if="word.last_wrong_time" class="last-wrong">上次错误: {{ word.last_wrong_time }}</span>
          </div>
        </div>
        <div class="word-actions">
          <button @click="removeWord(word.id)" class="action-btn remove-btn">移除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '../utils/api'

const router = useRouter()

const wrongWords = ref([])

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/login')
    return
  }
  
  try {
    const response = await userAPI.wrongWords()
    if (response.success) {
      wrongWords.value = response.data
    }
  } catch (error) {
    console.error('获取错题失败', error)
  }
})

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
}

const goBack = () => {
  router.push('/')
}

const removeWord = async (wordId) => {
  if (!confirm('确定要从错题本中移除这个单词吗？')) return
  
  try {
    const response = await userAPI.removeWrongWord(wordId)
    if (response.success) {
      wrongWords.value = wrongWords.value.filter(w => w.id !== wordId)
    }
  } catch (error) {
    console.error('移除失败', error)
  }
}
</script>

<style scoped>
.wrong-words-container {
  min-height: 100vh;
  background: #f5f7fa;
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
  color: #333;
}

.btn-back {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #f5f7fa;
}

.empty-state {
  max-width: 400px;
  margin: 0 auto;
  text-align: center;
  padding: 60px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state p {
  color: #666;
  font-size: 16px;
}

.words-list {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.word-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.word-info {
  flex: 1;
}

.word-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.word-header h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.level-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.level-1 { background: #e8f5e9; color: #2e7d32; }
.level-2 { background: #fff3e0; color: #e65100; }
.level-3 { background: #fce4ec; color: #c2185b; }

.meaning {
  color: #333;
  font-size: 16px;
  margin: 0 0 8px 0;
}

.phonetic {
  color: #999;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.example {
  color: #666;
  font-size: 14px;
  font-style: italic;
  margin: 0 0 12px 0;
}

.wrong-info {
  display: flex;
  gap: 20px;
}

.wrong-count, .last-wrong {
  font-size: 12px;
  color: #999;
}

.word-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.remove-btn {
  background: #ffebee;
  color: #f44336;
}

.remove-btn:hover {
  background: #ffcdd2;
}
</style>