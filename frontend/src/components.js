const Home = {
  template: `
    <div class="home-container">
      <header class="header">
        <div class="logo">
          <h1>📚 单词测评系统</h1>
          <p>检测您的英语词汇水平</p>
        </div>
        <nav class="nav">
          <button v-if="!isLoggedIn" @click="goTo('/login')" class="nav-btn">登录</button>
          <button v-if="!isLoggedIn" @click="goTo('/register')" class="nav-btn">注册</button>
          <button v-if="isLoggedIn" @click="goTo('/profile')" class="nav-btn user-btn">{{ user?.username }}</button>
          <button v-if="isLoggedIn" @click="logout" class="nav-btn">退出</button>
          <button @click="goTo('/admin/login')" class="nav-btn admin-btn">管理后台</button>
        </nav>
      </header>
      <main class="main-content">
        <section class="hero">
          <div class="hero-content">
            <h2>欢迎来到单词测评系统</h2>
            <p>通过智能测评算法，精准评估您的英语词汇水平</p>
            <div class="hero-buttons">
              <button @click="goTo('/test/start')" class="btn-primary">🚀 开始测评</button>
              <button @click="goTo('/history')" v-if="isLoggedIn" class="btn-secondary">📋 查看历史记录</button>
            </div>
          </div>
          <div class="hero-illustration">
            <div class="floating-card card-1">📝</div>
            <div class="floating-card card-2">📊</div>
            <div class="floating-card card-3">🎯</div>
          </div>
        </section>
        <section class="features">
          <h3>系统功能</h3>
          <div class="feature-cards">
            <div class="feature-card">
              <div class="icon">🧠</div>
              <h4>智能测评</h4>
              <p>基于答题情况动态调整难度，精准评估词汇水平</p>
            </div>
            <div class="feature-card">
              <div class="icon">📈</div>
              <h4>数据分析</h4>
              <p>详细的测评报告和学习进度分析</p>
            </div>
            <div class="feature-card">
              <div class="icon">📖</div>
              <h4>错题本</h4>
              <p>自动记录错题，支持重复练习</p>
            </div>
            <div class="feature-card">
              <div class="icon">📚</div>
              <h4>分级词库</h4>
              <p>小学、初中、高中三级词库，适合不同学段</p>
            </div>
          </div>
        </section>
        <section class="levels">
          <h3>选择词库开始测评</h3>
          <div class="level-cards">
            <div class="level-card level-1" @click="selectLevel(1)">
              <div class="level-icon">🌱</div>
              <h4>小学高频词汇</h4>
              <p>基础日常词汇，适合初学者</p>
              <span class="word-count">约20个单词</span>
            </div>
            <div class="level-card level-2" @click="selectLevel(2)">
              <div class="level-icon">🌿</div>
              <h4>初中高频词汇</h4>
              <p>常用核心词汇，夯实基础</p>
              <span class="word-count">约20个单词</span>
            </div>
            <div class="level-card level-3" @click="selectLevel(3)">
              <div class="level-icon">🌳</div>
              <h4>高中高频词汇</h4>
              <p>进阶词汇，提升阅读能力</p>
              <span class="word-count">约22个单词</span>
            </div>
          </div>
        </section>
      </main>
      <footer class="footer">
        <p>📖 单词测评系统 - 帮助您提升英语词汇能力</p>
      </footer>
    </div>
  `,
  data() {
    return {
      isLoggedIn: false,
      user: null
    }
  },
  mounted() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      this.user = JSON.parse(storedUser)
      this.isLoggedIn = true
    }
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      this.isLoggedIn = false
      this.user = null
      this.$router.push('/')
    },
    selectLevel(level) {
      localStorage.setItem('test_level', level)
      this.$router.push('/test/start')
    }
  }
}

const Login = {
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h2>🔐 用户登录</h2>
          <p>欢迎回来，请登录您的账号</p>
        </div>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="form.username" type="text" placeholder="请输入用户名" required>
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码" required>
          </div>
          <button type="submit" class="btn-primary">登录</button>
        </form>
        <div class="auth-links">
          <p>还没有账号？<a @click="goTo('/register')">立即注册</a></p>
          <p><a @click="goTo('/admin/login')">管理员登录</a></p>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    },
    async handleLogin() {
      try {
        const response = await axios.post(`${baseURL}/auth/login`, this.form)
        if (response.data.success) {
          localStorage.setItem('access_token', response.data.access_token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          this.$router.push('/')
        }
      } catch (error) {
        alert(error.response?.data?.message || '登录失败')
      }
    }
  }
}

const Register = {
  template: `
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h2>📝 用户注册</h2>
          <p>创建新账号，开始您的学习之旅</p>
        </div>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="form.username" type="text" placeholder="请输入用户名" required>
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码" required>
          </div>
          <div class="form-group">
            <label>邮箱（可选）</label>
            <input v-model="form.email" type="email" placeholder="请输入邮箱">
          </div>
          <button type="submit" class="btn-primary">注册</button>
        </form>
        <div class="auth-links">
          <p>已有账号？<a @click="goTo('/login')">立即登录</a></p>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      form: {
        username: '',
        password: '',
        email: ''
      }
    }
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    },
    async handleRegister() {
      try {
        const response = await axios.post(`${baseURL}/auth/register`, this.form)
        if (response.data.success) {
          alert('注册成功，请登录')
          this.$router.push('/login')
        }
      } catch (error) {
        alert(error.response?.data?.message || '注册失败')
      }
    }
  }
}

const TestStart = {
  template: `
    <div class="test-start-container">
      <div class="card">
        <div class="card-header">
          <h2>⚡ 选择测评模式</h2>
          <button @click="goBack" class="back-btn">← 返回首页</button>
        </div>
        <div class="mode-section">
          <h3>📚 词库选择</h3>
          <div class="level-options">
            <label v-for="level in levels" :key="level.value" class="level-option">
              <input type="radio" v-model="selectedLevel" :value="level.value">
              <div class="level-card-preview" :class="\`level-\${level.value}\`">
                <span class="level-icon">{{ level.icon }}</span>
                <span class="level-label">{{ level.label }}</span>
              </div>
            </label>
          </div>
        </div>
        <div class="mode-section">
          <h3>🎯 测评模式</h3>
          <div class="mode-options">
            <label class="mode-option">
              <input type="radio" v-model="testMode" value="basic">
              <div class="mode-card">
                <span class="mode-icon">📝</span>
                <div>
                  <span class="mode-title">基础测评</span>
                  <span class="mode-desc">适合初次测评，随机出题</span>
                </div>
              </div>
            </label>
            <label class="mode-option">
              <input type="radio" v-model="testMode" value="smart">
              <div class="mode-card">
                <span class="mode-icon">🧠</span>
                <div>
                  <span class="mode-title">智能测评</span>
                  <span class="mode-desc">结合错题本，个性化出题</span>
                </div>
              </div>
            </label>
          </div>
          <p v-if="testMode === 'smart' && !isLoggedIn" class="warning">⚠️ 智能测评需要登录账号</p>
        </div>
        <div class="button-group">
          <button @click="goBack" class="btn-secondary">返回</button>
          <button @click="startTest" class="btn-primary">开始测评</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      levels: [
        { value: 1, label: '小学高频词汇', icon: '🌱' },
        { value: 2, label: '初中高频词汇', icon: '🌿' },
        { value: 3, label: '高中高频词汇', icon: '🌳' }
      ],
      selectedLevel: 2,
      testMode: 'basic',
      isLoggedIn: false
    }
  },
  mounted() {
    const storedLevel = localStorage.getItem('test_level')
    if (storedLevel) {
      this.selectedLevel = parseInt(storedLevel)
      localStorage.removeItem('test_level')
    }
    if (localStorage.getItem('access_token')) {
      this.isLoggedIn = true
    }
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    async startTest() {
      localStorage.setItem('test_level', this.selectedLevel)
      localStorage.setItem('test_mode', this.testMode)
      try {
        let response
        if (this.testMode === 'smart' && this.isLoggedIn) {
          axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
          response = await axios.post(`${baseURL}/test/start/smart`, { level: this.selectedLevel })
        } else {
          response = await axios.post(`${baseURL}/test/start`, { level: this.selectedLevel, mode: 'basic' })
        }
        if (response.data.success) {
          localStorage.setItem('questions', JSON.stringify(response.data.questions))
          this.$router.push('/test')
        }
      } catch (error) {
        alert(error.response?.data?.message || '获取题目失败')
      }
    }
  }
}

const Test = {
  template: `
    <div class="test-container">
      <div class="test-header">
        <div class="progress">
          <span>📋 进度: {{ currentIndex + 1 }} / {{ questions.length }}</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
        <div class="timer">⏱️ {{ formatTime(elapsedTime) }}</div>
      </div>
      <div v-if="currentQuestion" class="question-card">
        <div class="question-header">
          <span class="question-type">{{ getQuestionTypeName(currentQuestion.question_type) }}</span>
          <span class="level-badge" :class="\`level-\${currentQuestion.level}\`">{{ getLevelName(currentQuestion.level) }}</span>
        </div>
        <div class="question-content">
          <h3>{{ currentQuestion.prompt }}</h3>
          <div v-if="currentQuestion.phonetic" class="phonetic">🔊 {{ currentQuestion.phonetic }}</div>
          <div v-if="currentQuestion.question_type === 'spelling'" class="spelling-input">
            <input v-model="userAnswer" type="text" placeholder="请输入单词拼写..." @keyup.enter="submitAnswer">
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
            <span v-if="isCorrect" class="correct-hint">✅ 回答正确！</span>
            <span v-else class="wrong-hint">❌ 回答错误，正确答案是：{{ getCorrectAnswer() }}</span>
          </div>
        </div>
        <div class="question-footer">
          <button v-if="showResult" @click="nextQuestion" class="btn-primary">
            {{ currentIndex < questions.length - 1 ? '➡️ 下一题' : '📤 提交测评' }}
          </button>
          <button v-else @click="submitAnswer" :disabled="!userAnswer" class="btn-primary" :class="{ disabled: !userAnswer }">
            ✅ 确认答案
          </button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      questions: [],
      currentIndex: 0,
      userAnswer: '',
      showResult: false,
      isCorrect: false,
      results: [],
      elapsedTime: 0
    }
  },
  computed: {
    progressPercent() {
      return ((this.currentIndex + 1) / this.questions.length) * 100
    },
    currentQuestion() {
      return this.questions[this.currentIndex]
    }
  },
  mounted() {
    const stored = localStorage.getItem('questions')
    if (stored) {
      this.questions = JSON.parse(stored)
    } else {
      this.$router.push('/test/start')
      return
    }
    this.timer = setInterval(() => {
      this.elapsedTime++
    }, 1000)
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  },
  methods: {
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    getQuestionTypeName(type) {
      const types = {
        choice_en: '看中文选英文',
        choice_zh: '看英文选中文',
        spelling: '单词拼写',
        recognition: '判断是否认识'
      }
      return types[type] || '未知类型'
    },
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    selectOption(key) {
      this.userAnswer = key
    },
    submitAnswer() {
      if (!this.userAnswer) return
      const correctOption = this.currentQuestion.options?.find(o => o.correct)
      const correctKey = correctOption?.key || this.currentQuestion.word
      let answerCorrect = false
      if (this.currentQuestion.question_type === 'spelling') {
        answerCorrect = this.userAnswer.toLowerCase() === this.currentQuestion.word.toLowerCase()
      } else if (this.currentQuestion.question_type === 'recognition') {
        answerCorrect = this.userAnswer === 'yes'
      } else {
        answerCorrect = correctOption && this.userAnswer === correctKey
      }
      this.isCorrect = answerCorrect
      this.showResult = true
      this.results.push({
        word_id: this.currentQuestion.word_id,
        word: this.currentQuestion.word,
        meaning: this.currentQuestion.meaning,
        user_answer: this.userAnswer,
        is_correct: answerCorrect,
        question_type: this.currentQuestion.question_type,
        level: this.currentQuestion.level
      })
    },
    getCorrectAnswer() {
      const correctOption = this.currentQuestion.options?.find(o => o.correct)
      return correctOption?.text || this.currentQuestion.word
    },
    async nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.userAnswer = ''
        this.showResult = false
      } else {
        await this.submitTest()
      }
    },
    async submitTest() {
      const level = parseInt(localStorage.getItem('test_level') || '2')
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
        }
        const response = await axios.post(`${baseURL}/test/submit`, {
          results: this.results,
          level: level
        })
        if (response.data.success) {
          localStorage.setItem('test_result', JSON.stringify(response.data))
          localStorage.removeItem('questions')
          localStorage.removeItem('test_level')
          this.$router.push('/test/result')
        }
      } catch (error) {
        alert(error.response?.data?.message || '提交失败')
      }
    }
  }
}

const TestResult = {
  template: `
    <div class="result-container">
      <div class="result-card">
        <div class="result-header">
          <div class="score-circle">
            <div class="score">{{ Math.round(result.analysis.overall.accuracy * 100) }}</div>
            <div class="score-label">正确率</div>
          </div>
        </div>
        <div class="result-info">
          <div class="info-row">
            <span class="info-label">测评结果</span>
            <span class="info-value level-badge" :class="\`level-\${result.estimated_level}\`">{{ result.level_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">总题数</span>
            <span class="info-value">{{ result.analysis.overall.total }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">正确数</span>
            <span class="info-value correct">✅ {{ result.analysis.overall.correct }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">错误数</span>
            <span class="info-value wrong">❌ {{ result.analysis.overall.total - result.analysis.overall.correct }}</span>
          </div>
        </div>
        <div class="level-analysis">
          <h3>📊 各学段表现</h3>
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
          <h3>💡 学习建议</h3>
          <ul>
            <li v-for="(suggestion, index) in suggestions" :key="index">{{ suggestion }}</li>
          </ul>
        </div>
        <div class="button-group">
          <button @click="goHome" class="btn-secondary">🏠 返回首页</button>
          <button @click="retest" class="btn-primary">🔄 再次测评</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      result: {
        analysis: {
          overall: { total: 0, correct: 0, accuracy: 0 },
          level_analysis: {}
        },
        estimated_level: 2,
        level_name: ''
      }
    }
  },
  computed: {
    suggestions() {
      const acc = this.result.analysis.overall.accuracy
      const level = this.result.estimated_level
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
    }
  },
  mounted() {
    const stored = localStorage.getItem('test_result')
    if (stored) {
      this.result = JSON.parse(stored)
    } else {
      this.$router.push('/test/start')
    }
  },
  methods: {
    getLevelColor(accuracy) {
      if (accuracy >= 0.8) return 'linear-gradient(135deg, #4caf50 0%, #81c784 100%)'
      if (accuracy >= 0.6) return 'linear-gradient(135deg, #ffb74d 0%, #ff9800 100%)'
      return 'linear-gradient(135deg, #f44336 0%, #ef9a9a 100%)'
    },
    goHome() {
      localStorage.removeItem('test_result')
      this.$router.push('/')
    },
    retest() {
      localStorage.removeItem('test_result')
      this.$router.push('/test/start')
    }
  }
}

const History = {
  template: `
    <div class="history-container">
      <div class="header">
        <h2>📋 测评历史记录</h2>
        <button @click="goBack" class="btn-back">← 返回</button>
      </div>
      <div v-if="records.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无测评记录</p>
        <button @click="goTest" class="btn-primary">开始测评</button>
      </div>
      <div v-else class="records-list">
        <div v-for="record in records" :key="record.id" class="record-card">
          <div class="record-header">
            <span class="level-badge" :class="\`level-\${record.level}\`">{{ getLevelName(record.level) }}</span>
            <span class="date">📅 {{ record.created_at }}</span>
          </div>
          <div class="record-stats">
            <div class="stat-item">
              <span class="stat-value">{{ Math.round(record.accuracy * 100) }}%</span>
              <span class="stat-label">正确率</span>
            </div>
            <div class="stat-item">
              <span class="stat-value correct">✅ {{ record.correct_count }}/{{ record.total_count }}</span>
              <span class="stat-label">正确数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value level-badge" :class="\`level-\${record.estimated_level}\`">{{ getLevelName(record.estimated_level) }}</span>
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
                <span class="summary-value level-badge" :class="\`level-\${detailData.record.estimated_level}\`">{{ getLevelName(detailData.record.estimated_level) }}</span>
              </div>
            </div>
            <div class="detail-questions">
              <h4>答题详情</h4>
              <div v-for="(detail, index) in detailData.details" :key="detail.id" class="question-detail">
                <div class="question-header">
                  <span class="question-num">第{{ index + 1 }}题</span>
                  <span :class="detail.is_correct ? 'correct-tag' : 'wrong-tag'">{{ detail.is_correct ? '✅ 正确' : '❌ 错误' }}</span>
                </div>
                <p><strong>{{ detail.word }}</strong> - {{ detail.meaning }}</p>
                <p v-if="!detail.is_correct" class="user-answer">你的答案: {{ detail.user_answer || '未作答' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      records: [],
      showDetail: false,
      detailData: null
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login')
      return
    }
    this.loadRecords()
  },
  methods: {
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    goBack() {
      this.$router.push('/')
    },
    goTest() {
      this.$router.push('/test/start')
    },
    async loadRecords() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/test/records`)
        if (response.data.success) {
          this.records = response.data.records
        }
      } catch (error) {
        console.error('获取记录失败', error)
      }
    },
    async viewDetail(id) {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/test/record/${id}`)
        if (response.data.success) {
          this.detailData = response.data
          this.showDetail = true
        }
      } catch (error) {
        console.error('获取详情失败', error)
      }
    },
    closeDetail() {
      this.showDetail = false
      this.detailData = null
    }
  }
}

const WrongWords = {
  template: `
    <div class="wrong-words-container">
      <div class="header">
        <h2>📖 错题本</h2>
        <button @click="goBack" class="btn-back">← 返回</button>
      </div>
      <div v-if="wrongWords.length === 0" class="empty-state">
        <div class="empty-icon">🎉</div>
        <p>太棒了！暂无错题</p>
        <button @click="goTest" class="btn-primary">继续测评</button>
      </div>
      <div v-else class="words-list">
        <div v-for="word in wrongWords" :key="word.id" class="word-card">
          <div class="word-info">
            <div class="word-header">
              <h3>{{ word.word }}</h3>
              <span class="level-badge" :class="\`level-\${word.level}\`">{{ getLevelName(word.level) }}</span>
            </div>
            <p class="meaning">{{ word.meaning }}</p>
            <p v-if="word.phonetic" class="phonetic">🔊 {{ word.phonetic }}</p>
            <p v-if="word.example" class="example">📝 {{ word.example }}</p>
            <div class="wrong-info">
              <span class="wrong-count">❌ 错误次数: {{ word.wrong_count }}</span>
              <span v-if="word.last_wrong_time" class="last-wrong">📅 上次错误: {{ word.last_wrong_time }}</span>
            </div>
          </div>
          <div class="word-actions">
            <button @click="removeWord(word.id)" class="action-btn remove-btn">移除</button>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      wrongWords: []
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login')
      return
    }
    this.loadWrongWords()
  },
  methods: {
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    goBack() {
      this.$router.push('/')
    },
    goTest() {
      this.$router.push('/test/start')
    },
    async loadWrongWords() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/user/wrong_words`)
        if (response.data.success) {
          this.wrongWords = response.data.data
        }
      } catch (error) {
        console.error('获取错题失败', error)
      }
    },
    async removeWord(wordId) {
      if (!confirm('确定要从错题本中移除这个单词吗？')) return
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.delete(`${baseURL}/user/wrong_words/${wordId}`)
        if (response.data.success) {
          this.wrongWords = this.wrongWords.filter(w => w.id !== wordId)
        }
      } catch (error) {
        console.error('移除失败', error)
      }
    }
  }
}

const Profile = {
  template: `
    <div class="profile-container">
      <div class="header">
        <h2>👤 个人中心</h2>
        <button @click="goBack" class="btn-back">← 返回</button>
      </div>
      <div class="profile-card">
        <div class="user-info">
          <div class="avatar">👤</div>
          <div class="user-details">
            <h3>{{ user?.username }}</h3>
            <p>{{ user?.email || '暂无邮箱' }}</p>
            <p class="join-date">📅 注册于 {{ user?.created_at }}</p>
          </div>
        </div>
      </div>
      <div class="stats-card">
        <h3>📊 学习统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.total_tests || 0 }}</span>
              <span class="stat-label">测评次数</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
              <span class="stat-value">{{ Math.round((stats.avg_accuracy || 0) * 100) }}%</span>
              <span class="stat-label">平均正确率</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">📅</div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.last_test_date || '-' }}</span>
              <span class="stat-label">上次测评</span>
            </div>
          </div>
        </div>
      </div>
      <div class="menu-card">
        <h3>🎯 功能菜单</h3>
        <div class="menu-items">
          <button @click="goTo('/history')" class="menu-item">
            <span class="menu-icon">📋</span>
            <span>测评历史</span>
            <span class="menu-arrow">→</span>
          </button>
          <button @click="goTo('/wrong-words')" class="menu-item">
            <span class="menu-icon">📖</span>
            <span>错题本</span>
            <span class="menu-arrow">→</span>
          </button>
          <button @click="goTo('/test/start')" class="menu-item">
            <span class="menu-icon">🎯</span>
            <span>开始测评</span>
            <span class="menu-arrow">→</span>
          </button>
        </div>
      </div>
      <div class="action-card">
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
    </div>
  `,
  data() {
    return {
      user: null,
      stats: {
        total_tests: 0,
        avg_accuracy: 0,
        last_test_date: null
      }
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login')
      return
    }
    this.loadData()
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    goTo(path) {
      this.$router.push(path)
    },
    async loadData() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const [userRes, statsRes] = await Promise.all([
          axios.get(`${baseURL}/auth/profile`),
          axios.get(`${baseURL}/user/stats`)
        ])
        if (userRes.data.success) {
          this.user = userRes.data.user
        }
        if (statsRes.data.success) {
          this.stats = statsRes.data.stats
        }
      } catch (error) {
        console.error('获取数据失败', error)
      }
    },
    logout() {
      if (!confirm('确定要退出登录吗？')) return
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      this.$router.push('/')
    }
  }
}

const AdminLogin = {
  template: `
    <div class="auth-container admin">
      <div class="auth-card">
        <div class="auth-header">
          <h2>🔒 管理员登录</h2>
          <p>请输入管理员账号</p>
        </div>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="form.username" type="text" placeholder="请输入用户名" required>
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码" required>
          </div>
          <button type="submit" class="btn-primary">登录</button>
        </form>
        <div class="auth-links">
          <p><a @click="goTo('/')">返回首页</a></p>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    },
    async handleLogin() {
      try {
        const response = await axios.post(`${baseURL}/auth/admin/login`, this.form)
        if (response.data.success) {
          localStorage.setItem('access_token', response.data.access_token)
          localStorage.setItem('admin', JSON.stringify(response.data.admin))
          this.$router.push('/admin')
        }
      } catch (error) {
        alert(error.response?.data?.message || '登录失败')
      }
    }
  }
}

const AdminDashboard = {
  template: `
    <div class="admin-container">
      <div class="sidebar">
        <div class="logo">
          <h2>⚙️ 管理后台</h2>
        </div>
        <nav class="nav">
          <button @click="goTo('/admin')" class="nav-item active">📊 仪表盘</button>
          <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
          <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
          <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
          <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
        </nav>
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
      <div class="main-content">
        <div class="header">
          <h1>📊 仪表盘</h1>
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
          <h3>📚 词库分级分布</h3>
          <div class="level-bars">
            <div v-for="(count, level) in stats.level_distribution" :key="level" class="level-bar-item">
              <span class="level-name">{{ getLevelName(level) }}</span>
              <div class="bar-container">
                <div class="bar-fill" :style="{ width: getBarWidth(count) + '%' }" :class="\`level-\${level}\`"></div>
              </div>
              <span class="bar-value">{{ count }}</span>
            </div>
          </div>
        </div>
        <div class="recent-tests">
          <h3>📝 最近测评记录</h3>
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
                <td><span class="level-badge" :class="\`level-\${record.level}\`">{{ getLevelName(record.level) }}</span></td>
                <td>{{ Math.round(record.accuracy * 100) }}%</td>
                <td><span class="level-badge" :class="\`level-\${record.estimated_level}\`">{{ getLevelName(record.estimated_level) }}</span></td>
                <td>{{ record.created_at }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      admin: null,
      stats: {
        user_count: 0,
        vocab_count: 0,
        test_count: 0,
        level_distribution: {},
        recent_tests: []
      }
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/admin/login')
      return
    }
    const stored = localStorage.getItem('admin')
    if (stored) {
      this.admin = JSON.parse(stored)
    }
    this.loadStats()
  },
  methods: {
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    getBarWidth(count) {
      const maxCount = Math.max(...Object.values(this.stats.level_distribution), 1)
      return (count / maxCount) * 100
    },
    async loadStats() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/admin/stats`)
        if (response.data.success) {
          this.stats = response.data.stats
        }
      } catch (error) {
        console.error('获取统计失败', error)
      }
    },
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('admin')
      this.$router.push('/admin/login')
    }
  }
}

const AdminUsers = {
  template: `
    <div class="admin-container">
      <div class="sidebar">
        <div class="logo">
          <h2>⚙️ 管理后台</h2>
        </div>
        <nav class="nav">
          <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
          <button @click="goTo('/admin/users')" class="nav-item active">👥 用户管理</button>
          <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
          <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
          <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
        </nav>
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
      <div class="main-content">
        <div class="header">
          <h1>👥 用户管理</h1>
          <div class="search-box">
            <input v-model="searchKeyword" type="text" placeholder="搜索用户名或邮箱" @keyup.enter="loadUsers">
            <button @click="loadUsers" class="search-btn">🔍 搜索</button>
          </div>
        </div>
        <div class="users-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>测评次数</th>
                <th>平均正确率</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email || '-' }}</td>
                <td>{{ user.test_count || 0 }}</td>
                <td>{{ Math.round((user.avg_accuracy || 0) * 100) }}%</td>
                <td>{{ user.created_at }}</td>
                <td>
                  <button @click="deleteUser(user.id)" class="delete-btn">🗑️ 删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button @click="prevPage" :disabled="currentPage <= 1" class="page-btn">← 上一页</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage >= totalPages" class="page-btn">下一页 →</button>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      users: [],
      searchKeyword: '',
      currentPage: 1,
      totalPages: 1
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/admin/login')
      return
    }
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/admin/users`, {
          params: {
            keyword: this.searchKeyword,
            page: this.currentPage,
            per_page: 20
          }
        })
        if (response.data.success) {
          this.users = response.data.data
          this.totalPages = Math.ceil(response.data.total / 20)
        }
      } catch (error) {
        console.error('获取用户失败', error)
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadUsers()
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.loadUsers()
      }
    },
    async deleteUser(id) {
      if (!confirm('确定要删除该用户吗？')) return
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.delete(`${baseURL}/admin/users/${id}`)
        if (response.data.success) {
          this.loadUsers()
        }
      } catch (error) {
        console.error('删除失败', error)
      }
    },
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('admin')
      this.$router.push('/admin/login')
    }
  }
}

const AdminVocab = {
  template: `
    <div class="admin-container">
      <div class="sidebar">
        <div class="logo">
          <h2>⚙️ 管理后台</h2>
        </div>
        <nav class="nav">
          <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
          <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
          <button @click="goTo('/admin/vocab')" class="nav-item active">📖 词库管理</button>
          <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
          <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
        </nav>
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
      <div class="main-content">
        <div class="header">
          <h1>📖 词库管理</h1>
          <button @click="showAddModal = true" class="add-btn">➕ 添加单词</button>
        </div>
        <div class="filter-bar">
          <select v-model="filterLevel" @change="loadVocab">
            <option value="">全部学段</option>
            <option value="1">小学</option>
            <option value="2">初中</option>
            <option value="3">高中</option>
          </select>
          <input v-model="searchKeyword" type="text" placeholder="搜索单词" @keyup.enter="loadVocab">
          <button @click="loadVocab" class="search-btn">🔍 搜索</button>
        </div>
        <div class="vocab-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>单词</th>
                <th>释义</th>
                <th>音标</th>
                <th>学段</th>
                <th>词频</th>
                <th>难度</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="word in vocabList" :key="word.id">
                <td>{{ word.id }}</td>
                <td>{{ word.word }}</td>
                <td>{{ word.meaning }}</td>
                <td>{{ word.phonetic || '-' }}</td>
                <td><span class="level-badge" :class="\`level-\${word.level}\`">{{ getLevelName(word.level) }}</span></td>
                <td>{{ word.frequency }}</td>
                <td>{{ word.difficulty }}</td>
                <td>
                  <button @click="editWord(word)" class="edit-btn">✏️ 编辑</button>
                  <button @click="deleteWord(word.id)" class="delete-btn">🗑️ 删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="showAddModal" class="modal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ editingWord ? '✏️ 编辑单词' : '➕ 添加单词' }}</h3>
              <button @click="closeModal" class="close-btn">×</button>
            </div>
            <form @submit.prevent="saveWord">
              <div class="form-group">
                <label>单词</label>
                <input v-model="form.word" type="text" required>
              </div>
              <div class="form-group">
                <label>释义</label>
                <input v-model="form.meaning" type="text" required>
              </div>
              <div class="form-group">
                <label>音标</label>
                <input v-model="form.phonetic" type="text">
              </div>
              <div class="form-group">
                <label>例句</label>
                <textarea v-model="form.example"></textarea>
              </div>
              <div class="form-group">
                <label>学段</label>
                <select v-model="form.level">
                  <option value="1">小学</option>
                  <option value="2">初中</option>
                  <option value="3">高中</option>
                </select>
              </div>
              <div class="form-group">
                <label>词频等级</label>
                <input v-model.number="form.frequency" type="number" min="1" max="5" value="3">
              </div>
              <div class="form-group">
                <label>难度等级</label>
                <input v-model.number="form.difficulty" type="number" min="1" max="5" value="3">
              </div>
              <button type="submit" class="submit-btn">保存</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      vocabList: [],
      filterLevel: '',
      searchKeyword: '',
      showAddModal: false,
      editingWord: null,
      form: {
        word: '',
        meaning: '',
        phonetic: '',
        example: '',
        level: '2',
        frequency: 3,
        difficulty: 3
      }
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/admin/login')
      return
    }
    this.loadVocab()
  },
  methods: {
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    async loadVocab() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const params = {}
        if (this.filterLevel) params.level = this.filterLevel
        if (this.searchKeyword) params.keyword = this.searchKeyword
        const response = await axios.get(`${baseURL}/vocab/search`, { params })
        if (response.data.success) {
          this.vocabList = response.data.data
        }
      } catch (error) {
        console.error('获取词库失败', error)
      }
    },
    editWord(word) {
      this.editingWord = word
      this.form = {
        word: word.word,
        meaning: word.meaning,
        phonetic: word.phonetic || '',
        example: word.example || '',
        level: String(word.level),
        frequency: word.frequency,
        difficulty: word.difficulty
      }
      this.showAddModal = true
    },
    async deleteWord(id) {
      if (!confirm('确定要删除该单词吗？')) return
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.delete(`${baseURL}/vocab/${id}`)
        if (response.data.success) {
          this.loadVocab()
        }
      } catch (error) {
        console.error('删除失败', error)
      }
    },
    closeModal() {
      this.showAddModal = false
      this.editingWord = null
      this.form = {
        word: '',
        meaning: '',
        phonetic: '',
        example: '',
        level: '2',
        frequency: 3,
        difficulty: 3
      }
    },
    async saveWord() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        if (this.editingWord) {
          await axios.put(`${baseURL}/vocab/${this.editingWord.id}`, this.form)
        } else {
          await axios.post(`${baseURL}/vocab/add`, this.form)
        }
        this.closeModal()
        this.loadVocab()
      } catch (error) {
        console.error('保存失败', error)
      }
    },
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('admin')
      this.$router.push('/admin/login')
    }
  }
}

const AdminRecords = {
  template: `
    <div class="admin-container">
      <div class="sidebar">
        <div class="logo">
          <h2>⚙️ 管理后台</h2>
        </div>
        <nav class="nav">
          <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
          <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
          <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
          <button @click="goTo('/admin/records')" class="nav-item active">📝 测评记录</button>
          <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
        </nav>
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
      <div class="main-content">
        <div class="header">
          <h1>📝 测评记录</h1>
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
                <td><span class="level-badge" :class="\`level-\${record.level}\`">{{ getLevelName(record.level) }}</span></td>
                <td>{{ record.total_count }}</td>
                <td>{{ record.correct_count }}</td>
                <td>{{ Math.round(record.accuracy * 100) }}%</td>
                <td><span class="level-badge" :class="\`level-\${record.estimated_level}\`">{{ getLevelName(record.estimated_level) }}</span></td>
                <td>{{ record.created_at }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      records: []
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/admin/login')
      return
    }
    this.loadRecords()
  },
  methods: {
    getLevelName(level) {
      const levels = { 1: '小学', 2: '初中', 3: '高中' }
      return levels[level] || '未知'
    },
    async loadRecords() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/admin/stats`)
        if (response.data.success) {
          this.records = response.data.stats.recent_tests
        }
      } catch (error) {
        console.error('获取记录失败', error)
      }
    },
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('admin')
      this.$router.push('/admin/login')
    }
  }
}

const AdminStats = {
  template: `
    <div class="admin-container">
      <div class="sidebar">
        <div class="logo">
          <h2>⚙️ 管理后台</h2>
        </div>
        <nav class="nav">
          <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
          <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
          <button @click="goTo('/admin/vocab')" class="nav-item">📖 词库管理</button>
          <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
          <button @click="goTo('/admin/stats')" class="nav-item active">📈 数据统计</button>
        </nav>
        <button @click="logout" class="logout-btn">🚪 退出登录</button>
      </div>
      <div class="main-content">
        <div class="header">
          <h1>📈 数据统计</h1>
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
          <h3>📚 词库分级统计</h3>
          <div id="levelChart" style="height: 300px;"></div>
        </div>
        <div class="chart-section">
          <h3>📊 测评等级分布</h3>
          <div id="levelDistChart" style="height: 300px;"></div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      stats: {
        user_count: 0,
        vocab_count: 0,
        test_count: 0,
        level_distribution: {}
      }
    }
  },
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/admin/login')
      return
    }
    this.loadStats()
  },
  methods: {
    async loadStats() {
      try {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('access_token')
        const response = await axios.get(`${baseURL}/admin/stats`)
        if (response.data.success) {
          this.stats = response.data.stats
          setTimeout(() => {
            this.initCharts()
          }, 100)
        }
      } catch (error) {
        console.error('获取统计失败', error)
      }
    },
    initCharts() {
      const levelChart = echarts.init(document.getElementById('levelChart'))
      const levelDistChart = echarts.init(document.getElementById('levelDistChart'))
      const levelData = [
        { value: this.stats.level_distribution[1] || 0, name: '小学' },
        { value: this.stats.level_distribution[2] || 0, name: '初中' },
        { value: this.stats.level_distribution[3] || 0, name: '高中' }
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
      if (this.stats.recent_tests) {
        this.stats.recent_tests.forEach(record => {
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
    },
    goTo(path) {
      this.$router.push(path)
    },
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('admin')
      this.$router.push('/admin/login')
    }
  }
}