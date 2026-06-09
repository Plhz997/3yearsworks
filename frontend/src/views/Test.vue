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
        <div class="countdown-bar-wrapper">
          <div class="countdown-bar" :style="formatTimerBar"></div>
        </div>
        <span class="countdown-text" :class="{ 'countdown-warn': questionTime <= 3 }">
          ⏳ {{ questionTime }}s
        </span>
        <span class="level-badge" :class="`level-${currentQuestion.level}`">{{ getLevelName(currentQuestion.level) }}</span>
      </div>
      
      <div class="question-content">
        <h3>
          {{ currentQuestion.prompt }}
          <button @click="speakWord(currentQuestion.word)" class="speak-btn" title="点击朗读单词">
            🔊
          </button>
        </h3>
        
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
          <span v-else-if="userAnswer === 'unknown'" class="unknown-hint">🔍 这个单词的意思是：{{ currentQuestion.meaning }}</span>
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
const questionTime = ref(0)
const questionTimeLimit = ref(10)
const consecutiveWrong = ref(0)
const totalWrong = ref(0)
let timer = null
let questionTimer = null

// 题型限时（秒）
const TIME_LIMITS = {
  spelling: 20,
  choice_en: 10,
  choice_zh: 10,
  recognition: 5
}

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
  
  startQuestionTimer()
  
  // 自动朗读第一个单词
  setTimeout(() => {
    if (currentQuestion.value) {
      speakWord(currentQuestion.value.word)
    }
  }, 500)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (questionTimer) clearInterval(questionTimer)
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

const speakWord = (text) => {
  if (!text || !window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  utterance.rate = 0.85
  utterance.pitch = 1.0
  window.speechSynthesis.speak(utterance)
}

const startQuestionTimer = () => {
  if (!currentQuestion.value) return
  const qtype = currentQuestion.value.question_type
  questionTimeLimit.value = TIME_LIMITS[qtype] || 10
  questionTime.value = questionTimeLimit.value
  
  if (questionTimer) clearInterval(questionTimer)
  questionTimer = setInterval(() => {
    questionTime.value--
    if (questionTime.value <= 0) {
      clearInterval(questionTimer)
      if (!showResult.value) {
        // 超时 - 自动提交为错
        const qtype = currentQuestion.value.question_type
        if (qtype === 'recognition') {
          userAnswer.value = 'no'
        } else if (!userAnswer.value) {
          userAnswer.value = 'timeout'
        }
        submitAnswer()
      }
    }
  }, 1000)
}

const stopQuestionTimer = () => {
  if (questionTimer) {
    clearInterval(questionTimer)
    questionTimer = null
  }
}

const formatTimerBar = computed(() => {
  const pct = (questionTime.value / questionTimeLimit.value) * 100
  return { width: pct + '%', background: questionTime.value <= 3 ? 'var(--danger-color)' : questionTime.value <= 5 ? '#ff9800' : 'var(--accent-primary)' }
})

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
  // 选择题和认识题：选择后自动提交
  const qtype = currentQuestion.value.question_type
  if (qtype !== 'spelling') {
    submitAnswer()
    // 显示结果后自动跳转下一题
    setTimeout(() => {
      if (showResult.value) {
        nextQuestion()
      }
    }, 800)
  }
}

const submitAnswer = () => {
  if (!userAnswer.value) return
  
  stopQuestionTimer()
  
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
  
  if (!answerCorrect) {
    consecutiveWrong.value++
    totalWrong.value++
  } else {
    consecutiveWrong.value = 0
  }
  
  results.value.push({
    word_id: currentQuestion.value.word_id,
    word: currentQuestion.value.word,
    meaning: currentQuestion.value.meaning,
    user_answer: userAnswer.value,
    is_correct: answerCorrect,
    question_type: currentQuestion.value.question_type,
    level: currentQuestion.value.level,
    difficulty_level: currentQuestion.value.difficulty_level
  })
}

const getCorrectAnswer = () => {
  const correctOption = currentQuestion.value.options?.find(o => o.correct)
  return correctOption?.text || currentQuestion.value.word
}

const nextQuestion = async () => {
  if (consecutiveWrong.value >= 4) {
    alert('连续答错4题，测评结束！')
    await submitTest()
    return
  }
  if (totalWrong.value >= 7) {
    alert('累计答错7题，测评结束！')
    await submitTest()
    return
  }
  
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
    userAnswer.value = ''
    showResult.value = false
    setTimeout(() => speakWord(currentQuestion.value.word), 300)
    startQuestionTimer()
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
  background: var(--bg-primary);
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
  color: var(--text-primary);
}

.progress-bar {
  width: 300px;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  margin-top: 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 4px;
  transition: width 0.3s;
}

.timer {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent-primary);
}

.question-card {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px;
  box-shadow: var(--shadow);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 10px;
}

.question-type {
  background: var(--accent-primary);
  color: var(--text-light);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.countdown-bar-wrapper {
  flex: 1;
  max-width: 200px;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.countdown-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 1s linear, background 0.3s;
}

.countdown-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 45px;
  text-align: center;
}

.countdown-warn {
  color: var(--danger-color);
  animation: pulse 0.5s ease-in-out infinite alternate;
}

@keyframes pulse {
  from { opacity: 1; }
  to { opacity: 0.5; }
}

.level-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
}

.level-1 { background: var(--level-1-bg); color: var(--level-1-color); }
.level-2 { background: var(--level-2-bg); color: var(--level-2-color); }
.level-3 { background: var(--level-3-bg); color: var(--level-3-color); }

.question-content h3 {
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 24px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.speak-btn {
  background: var(--info-bg);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.speak-btn:hover {
  background: var(--info-color);
  color: white;
  transform: scale(1.1);
}

.speak-btn:active {
  transform: scale(0.95);
}

.phonetic {
  text-align: center;
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 24px;
}

.spelling-input input {
  width: 100%;
  padding: 16px;
  font-size: 20px;
  text-align: center;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  outline: none;
  background: var(--input-bg);
  color: var(--text-primary);
  transition: all 0.3s;
}

.spelling-input input:focus {
  border-color: var(--accent-primary);
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
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s;
}

.recognition-btn:hover {
  border-color: var(--accent-primary);
}

.recognition-btn.selected {
  background: var(--accent-primary);
  color: var(--text-light);
  border-color: var(--accent-primary);
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
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s;
}

.option-btn:hover {
  border-color: var(--accent-primary);
}

.option-btn.selected {
  border-color: var(--accent-primary);
  background: var(--btn-secondary-bg);
}

.option-btn.correct {
  background: var(--success-bg);
  border-color: #4caf50;
  color: var(--success-color);
}

.option-btn.wrong {
  background: var(--danger-bg);
  border-color: var(--danger-color);
  color: var(--danger-color);
}

.option-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--btn-secondary-bg);
  border-radius: 50%;
  font-weight: 600;
  color: var(--text-secondary);
}

.result-hint {
  text-align: center;
  margin-top: 24px;
  font-size: 18px;
  font-weight: 600;
}

.correct-hint {
  color: var(--success-color);
}

.wrong-hint {
  color: var(--danger-color);
}

.unknown-hint {
  color: var(--info-color);
}

.question-footer {
  margin-top: 32px;
  text-align: center;
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
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