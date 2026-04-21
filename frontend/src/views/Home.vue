<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">
        <h1>单词测评系统</h1>
        <p>检测您的英语词汇水平</p>
      </div>
      <nav class="nav">
        <button v-if="!isLoggedIn" @click="goTo('/login')" class="nav-btn">登录</button>
        <button v-if="!isLoggedIn" @click="goTo('/register')" class="nav-btn">注册</button>
        <button v-if="isLoggedIn" @click="goTo('/wrong-words')" class="nav-btn">错题本</button>
        <button v-if="isLoggedIn" @click="goTo('/profile')" class="nav-btn">{{ user?.username }}</button>
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
            <button @click="goTo('/test/start')" class="btn-primary">开始测评</button>
            <button @click="goTo('/history')" v-if="isLoggedIn" class="btn-secondary">查看历史记录</button>
          </div>
        </div>
      </section>

      <section class="features">
        <h3>系统功能</h3>
        <div class="feature-cards">
          <div class="feature-card">
            <div class="icon">📝</div>
            <h4>智能测评</h4>
            <p>基于答题情况动态调整难度，精准评估词汇水平</p>
          </div>
          <div class="feature-card">
            <div class="icon">📊</div>
            <h4>数据分析</h4>
            <p>详细的测评报告和学习进度分析</p>
          </div>
          <div class="feature-card clickable" @click="goTo('/wrong-words')">
            <div class="icon">📖</div>
            <h4>错题本</h4>
            <p>自动记录错题，支持重复练习</p>
          </div>
          <div class="feature-card">
            <div class="icon">🎯</div>
            <h4>分级词库</h4>
            <p>小学、初中、高中三级词库，适合不同学段</p>
          </div>
        </div>
      </section>

      <section class="levels">
        <h3>词库分级</h3>
        <div class="level-cards">
          <div class="level-card level-1" @click="selectLevel(1)">
            <h4>小学高频词汇</h4>
            <p>基础日常词汇，适合初学者</p>
            <span class="word-count">约60个单词</span>
          </div>
          <div class="level-card level-2" @click="selectLevel(2)">
            <h4>初中高频词汇</h4>
            <p>常用核心词汇，夯实基础</p>
            <span class="word-count">约90个单词</span>
          </div>
          <div class="level-card level-3" @click="selectLevel(3)">
            <h4>高中高频词汇</h4>
            <p>进阶词汇，提升阅读能力</p>
            <span class="word-count">约100个单词</span>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>单词测评系统 - 帮助您提升英语词汇能力</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = ref(false)
const user = ref(null)

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    user.value = JSON.parse(storedUser)
    isLoggedIn.value = true
  }
})

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  isLoggedIn.value = false
  user.value = null
  router.push('/')
}

const selectLevel = (level) => {
  localStorage.setItem('test_level', level)
  router.push('/test/start')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.logo h1 {
  color: white;
  font-size: 24px;
  margin: 0;
}

.logo p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 4px 0 0 0;
}

.nav {
  display: flex;
  gap: 15px;
}

.nav-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.admin-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

.admin-btn:hover {
  background: white;
}

.main-content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 60px 0;
}

.hero-content h2 {
  color: white;
  font-size: 42px;
  margin-bottom: 16px;
}

.hero-content p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  margin-bottom: 32px;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.btn-primary {
  background: white;
  color: #667eea;
  padding: 14px 32px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 14px 32px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  border: 2px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.features, .levels {
  background: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
}

.features h3, .levels h3 {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 32px;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card.clickable:hover {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eaf6 100%);
}

.icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-card h4 {
  color: #333;
  font-size: 18px;
  margin-bottom: 8px;
}

.feature-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.level-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.level-card {
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.level-card:hover {
  transform: translateY(-5px);
}

.level-1 {
  background: linear-gradient(135deg, #81c784 0%, #4caf50 100%);
}

.level-2 {
  background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%);
}

.level-3 {
  background: linear-gradient(135deg, #f48fb1 0%, #e91e63 100%);
}

.level-card h4 {
  color: white;
  font-size: 20px;
  margin-bottom: 8px;
}

.level-card p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-bottom: 12px;
}

.word-count {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 16px;
  border-radius: 20px;
  color: white;
  font-size: 12px;
}

.footer {
  text-align: center;
  padding: 30px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}
</style>