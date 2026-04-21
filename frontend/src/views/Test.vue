<template>
  <div class="test-container">
    <div class="test-header">
      <div class="progress">
        <span>进度: {{ currentIndex + 1 }} / {{ questions.length }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
      <div class="timer">⏱️ {{ formatTime(elapsedTime) }}</div>
    </div>

    <div v-if="currentQuestion" class="question-card">
      <div class="question-header">
        <span class="question-type">{{ getQuestionTypeName(currentQuestion.question_type) }}</span>
        <span class="level-badge" :class="`level-${currentQuestion.level}`">{{ getLevelName(currentQuestion.level) }}</span>
      </div>
      
      <div class="question-content">
        <h3>{{ currentQuestion.prompt }}</h3>
        
        <div v-if="currentQuestion.phonetic" class="phonetic">{{ currentQuestion.phonetic }}</div>
        
        <div v-if="currentQuestion.question_type === 'spelling'" class="spelling-input">
          <input v-model="userAnswer" type="text" placeholder="请输入单词拼写" @keyup.enter="submitAnswer">
        </div>
        
        <div v-else-if="currentQuestion.question_type === 'recognition'" class="recognition-options">
          <button 
            v-for="option in currentQuestion.options" 
            :key="option.key"
            @click="selectOption(option.key)"
            class="recognition-btn"
            :class="{ selected: userAnswer === option.key }"
          >
            {{ option.text }}
          </button>
        </div>
        
        <div v-else class="options">
          <button 
            v-for="(option, index) in currentQuestion.options" 
            :key="option.key"
            @click="selectOption(option.key)"
            class="option-btn"
            :class="{ selected: userAnswer === option.key, correct: showResult && option.correct, wrong: showResult && userAnswer === option.key && !option.correct }"
          >
            <span class="option-index">{{ String.fromCharCode(65 + index) }}</span>
            <span>{{ option.text }}</span>
          </button>
        </div>
        
        <div v-if="showResult" class="result-hint">
          <span v-if="isCorrect" class="correct-hint">✓ 回答正确！</span>
          <span v-else-if="currentQuestion.question_type === 'recognition' && userAnswer === 'no'" class="unknown-hint">🔍 这个单词的意思是：{{ currentQuestion.meaning }}</span>
          <span v-else class="wrong-hint">✗ 回答错误，正确答案是：{{ getCorrectAnswer() }}</span>
        </div>
      </div>
      
      <div class="question-footer">
        <button v-if="showResult" @click="nextQuestion" class="btn-primary">
          {{ currentIndex < questions.length - 1 ? '下一题' : '提交测评' }}
          <span class="key-hint">Enter</span>
        </button>
        <button v-else @click="submitAnswer" :disabled="!userAnswer" class="btn-primary" :class="{ disabled: !userAnswer }">
          确认答案
          <span v-if="userAnswer" class="key-hint">Enter</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { testAPI } from '../utils/api'

const router = useRouter()

const questions = ref([])
const currentIndex = ref(0)
const userAnswer = ref('')
const showResult = ref(false)
const isCorrect = ref(false)
const results = ref([])
const elapsedTime = ref(0)
let timer = null

const progressPercent = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100)

const currentQuestion = computed(() => questions.value[currentIndex.value])

onMounted(() => {
  const stored = localStorage.getItem('questions')
  if (stored) {
    questions.value = JSON.parse(stored)
  } else {
    router.push('/test/start')
    return
  }
  
  timer = setInterval(() => {
    elapsedTime.value++
  }, 1000)
  
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('keydown', handleKeydown)
})

const handleKeydown = (e) => {
  if (e.key === 'Enter') {
    e.preventDefault()
    if (showResult.value) {
      nextQuestion()
    } else if (userAnswer.value) {
      submitAnswer()
    }
  }
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getQuestionTypeName = (type) => {
  const types = {
    choice_en: '看中文选英文',
    choice_zh: '看英文选中文',
    spelling: '单词拼写',
    recognition: '判断是否认识'
  }
  return types[type] || '未知类型'
}

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
}

const selectOption = (key) => {
  userAnswer.value = key
}

const submitAnswer = () => {
  if (!userAnswer.value) return
  
  const correctOption = currentQuestion.value.options?.find(o => o.correct)
  const correctKey = correctOption?.key || currentQuestion.value.word
  
  let answerCorrect = false
  if (currentQuestion.value.question_type === 'spelling') {
    answerCorrect = userAnswer.value.toLowerCase() === currentQuestion.value.word.toLowerCase()
  } else if (currentQuestion.value.question_type === 'recognition') {
    answerCorrect = userAnswer.value === 'yes'
  } else {
    answerCorrect = correctOption && userAnswer.value === correctKey
  }
  
  isCorrect.value = answerCorrect
  showResult.value = true
  
  results.value.push({
    word_id: currentQuestion.value.word_id,
    word: currentQuestion.value.word,
    meaning: currentQuestion.value.meaning,
    user_answer: userAnswer.value,
    is_correct: answerCorrect,
    question_type: currentQuestion.value.question_type,
    level: currentQuestion.value.level
  })
}

const getCorrectAnswer = () => {
  const correctOption = currentQuestion.value.options?.find(o => o.correct)
  return correctOption?.text || currentQuestion.value.word
}

const nextQuestion = async () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    userAnswer.value = ''
    showResult.value = false
  } else {
    await submitTest()
  }
}

const submitTest = async () => {
  const level = parseInt(localStorage.getItem('test_level') || '2')
  
  try {
    const response = await testAPI.submit({
      results: results.value,
      level: level
    })
    
    if (response.data.success) {
      localStorage.setItem('test_result', JSON.stringify(response.data))
      localStorage.removeItem('questions')
      localStorage.removeItem('test_level')
      router.push('/test/result')
    }
  } catch (error) {
    alert(error.response?.data?.message || '提交失败')
  }
}
</script>

<style scoped>
.test-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.test-header {
  max-width: 800px;
  margin: 0 auto 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress span {
  font-weight: 600;
  color: #333;
}

.progress-bar {
  width: 300px;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  margin-top: 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s;
}

.timer {
  font-size: 18px;
  font-weight: 600;
  color: #667eea;
}

.question-card {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.question-type {
  background: #667eea;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.level-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.level-1 { background: #e8f5e9; color: #2e7d32; }
.level-2 { background: #fff3e0; color: #e65100; }
.level-3 { background: #fce4ec; color: #c2185b; }

.question-content h3 {
  font-size: 24px;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}

.phonetic {
  text-align: center;
  color: #999;
  font-size: 16px;
  margin-bottom: 24px;
}

.spelling-input input {
  width: 100%;
  padding: 16px;
  font-size: 20px;
  text-align: center;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s;
}

.spelling-input input:focus {
  border-color: #667eea;
}

.recognition-options {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.recognition-btn {
  padding: 20px 60px;
  font-size: 18px;
  font-weight: 600;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.recognition-btn:hover {
  border-color: #667eea;
}

.recognition-btn.selected {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  font-size: 18px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.option-btn:hover {
  border-color: #667eea;
}

.option-btn.selected {
  border-color: #667eea;
  background: #f5f7ff;
}

.option-btn.correct {
  background: #e8f5e9;
  border-color: #4caf50;
  color: #2e7d32;
}

.option-btn.wrong {
  background: #ffebee;
  border-color: #f44336;
  color: #c62828;
}

.option-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #f5f7fa;
  border-radius: 50%;
  font-weight: 600;
  color: #666;
}

.result-hint {
  text-align: center;
  margin-top: 24px;
  font-size: 18px;
  font-weight: 600;
}

.correct-hint {
  color: #4caf50;
}

.wrong-hint {
  color: #f44336;
}

.unknown-hint {
  color: #2196f3;
}

.question-footer {
  margin-top: 32px;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px 48px;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.key-hint {
  font-size: 12px;
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 500;
}
</style>