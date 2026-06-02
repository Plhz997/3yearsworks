<template>
  <div class="home-container" :class="themeClass">
    <header class="header">
      <div class="logo">
        <h1>单词测评系统</h1>
        <p>检测您的英语词汇水平</p>
      </div>
      <nav class="nav">
        <button v-if="!isLoggedIn" @click="goTo('/login')" class="nav-btn">登录</button>
        <button v-if="!isLoggedIn" @click="goTo('/register')" class="nav-btn">注册</button>
        <button v-if="isLoggedIn" @click="goTo('/wrong-words')" class="nav-btn">错题本</button>
        <button @click="goTo('/companion-shop')" class="nav-btn">咖啡豆商店</button>
        <button @click="quickChangeTheme" class="nav-btn">一键换肤</button>
        <button v-if="isLoggedIn" @click="goTo('/profile')" class="nav-btn">{{ user?.username }}</button>
        <button v-if="isLoggedIn" @click="logout" class="nav-btn">退出</button>
        <button @click="goTo('/admin/login')" class="nav-btn admin-btn">管理后台</button>
      </nav>
    </header>

    <main class="main-content">
      <section class="study-desktop">
        <div class="desktop-main">
          <p class="desktop-eyebrow">TODAY STUDY DESK</p>
          <h2>{{ greetingTitle }}</h2>
          <p>{{ deskSubtitle }}</p>
          <div class="hero-buttons">
            <button @click="goTo('/pomodoro')" class="btn-primary">进入咖啡馆专注模式</button>
            <button @click="goTo('/test/start')" class="btn-secondary">开始测评</button>
            <button @click="goTo('/history')" v-if="isLoggedIn" class="btn-secondary">查看历史记录</button>
          </div>
        </div>
        <div class="desktop-card">
          <div class="plan-row">
            <span>今日计划</span>
            <strong>新词 {{ todayPlan.newWords }} 个，错词 {{ todayPlan.wrongWords }} 个</strong>
          </div>
          <div class="plan-row">
            <span>今日专注</span>
            <strong>{{ gameState.todayFocusCount }} / {{ todayPlan.targetPomodoros }} 个番茄钟</strong>
          </div>
          <div class="plan-row">
            <span>今日咖啡</span>
            <strong>{{ coffeeStatus }}</strong>
          </div>
          <div class="plan-row warning">
            <span>错词提醒</span>
            <strong>还有 {{ wrongWordCount }} 个词需要复习</strong>
          </div>
          <div class="skill-reminders">
            <button
              v-for="item in skillReminders"
              :key="item.id"
              @click="startSkillTask(item.id)"
            >
              <span>{{ item.icon }}</span>
              <strong>{{ item.name }}</strong>
              <small>{{ item.target }}</small>
            </button>
          </div>
          <div class="desktop-progress">
            <i :style="{ width: desktopProgress + '%' }"></i>
          </div>
          <div class="companion-row">
            <div class="desktop-pet">
              <PetAvatar :pet-id="gameState.equippedPet" size="small" :mood="companionState.mood" />
            </div>
            <div>
              <strong>{{ companionState.label }}</strong>
              <p>{{ companionState.message }}</p>
            </div>
          </div>
          <small>完成今日桌面任务可继续积累咖啡豆和能量值</small>
        </div>
      </section>

      <section class="features">
        <h3>系统功能</h3>
        <div class="feature-cards">
          <div class="feature-card clickable" @click="goTo('/test/start')">
            <div class="icon">📝</div>
            <h4>智能测评</h4>
            <p>基于答题情况动态调整难度，精准评估词汇水平</p>
          </div>
          <div class="feature-card clickable" @click="goTo('/history')">
            <div class="icon">📊</div>
            <h4>数据分析</h4>
            <p>详细的测评报告和学习进度分析</p>
          </div>
          <div class="feature-card clickable" @click="goTo('/wrong-words')">
            <div class="icon">📖</div>
            <h4>错题本</h4>
            <p>自动记录错题，支持重复练习</p>
          </div>
          <div class="feature-card clickable" @click="goTo('/pomodoro')">
            <div class="icon">🍅</div>
            <h4>番茄伴学</h4>
            <p>沉浸式专注计时，支持单词、阅读、精听和跟读</p>
          </div>
          <div class="feature-card clickable" @click="goTo('/companion-shop')">
            <div class="icon">☕</div>
            <h4>咖啡豆商店</h4>
            <p>兑换宠物、头像框和学习壁纸</p>
          </div>
        </div>
      </section>

      <section class="levels">
        <h3>词库分级</h3>
        <div class="level-cards">
          <div class="level-card level-1" @click="selectLevel(1)">
            <h4>小学高频词汇</h4>
            <p>基础日常词汇，适合初学者</p>
            <span class="word-count">约500个单词</span>
          </div>
          <div class="level-card level-2" @click="selectLevel(2)">
            <h4>初中高频词汇</h4>
            <p>常用核心词汇，夯实基础</p>
            <span class="word-count">约1500个单词</span>
          </div>
          <div class="level-card level-3" @click="selectLevel(3)">
            <h4>高中高频词汇</h4>
            <p>进阶词汇，提升阅读能力</p>
            <span class="word-count">约3500个单词</span>
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
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '../utils/api'
import PetAvatar from '../components/PetAvatar.vue'
import { equipItem, loadGameState, resolveCompanionState, shopCatalog } from '../utils/gamification'

const router = useRouter()
const isLoggedIn = ref(false)
const user = ref(null)
const gameState = ref(loadGameState())
const wrongWordCount = ref(8)
const todayPlan = ref({
  newWords: 20,
  wrongWords: 10,
  targetPomodoros: 2
})
const skillReminders = [
  { id: 'reading', icon: '📚', name: '阅读理解', target: '1 篇限时阅读' },
  { id: 'cloze7', icon: '🧩', name: '七选五', target: '1 组逻辑训练' },
  { id: 'listening', icon: '🎧', name: '英语精听', target: '5 步精听复盘' },
  { id: 'shadowing', icon: '🎙️', name: '影子跟读', target: '6 步跟读训练' }
]

const greetingTitle = computed(() => {
  if (user.value?.username) return `${user.value.username}，今天从这张学习桌开始`
  return '今日学习桌面'
})

const deskSubtitle = computed(() => {
  if (gameState.value.todayFocusCount >= todayPlan.value.targetPomodoros) return '今天的番茄钟目标已经完成，可以轻量复习错词。'
  return '先完成一轮咖啡馆专注，再回来做测评或错词复习。'
})

const coffeeStatus = computed(() => {
  if (gameState.value.todayFocusCount >= todayPlan.value.targetPomodoros) return '已完成'
  if (gameState.value.todayFocusCount > 0) return '进行中'
  return '未完成'
})

const desktopProgress = computed(() => {
  return Math.min(100, Math.round((gameState.value.todayFocusCount / todayPlan.value.targetPomodoros) * 100))
})
const companionState = computed(() => resolveCompanionState({
  wrongCount: wrongWordCount.value,
  gameState: gameState.value
}))
const themeClass = computed(() => `theme-${gameState.value.equippedTheme || 'theme_classic'}`)

onMounted(async () => {
  gameState.value = loadGameState()
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    user.value = JSON.parse(storedUser)
    isLoggedIn.value = true
  }

  if (isLoggedIn.value) {
    try {
      const response = await userAPI.wrongWords()
      if (response.data.success) {
        const words = response.data.wrong_words || response.data.data || []
        wrongWordCount.value = words.length || wrongWordCount.value
        todayPlan.value.wrongWords = Math.min(15, Math.max(5, wrongWordCount.value))
      }
    } catch (error) {
      console.error('获取错词提醒失败', error)
    }
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

const startSkillTask = (taskId) => {
  localStorage.setItem('pomodoro_task', taskId)
  router.push('/pomodoro')
}

const quickChangeTheme = () => {
  const ownedThemes = shopCatalog.filter((item) => item.type === 'theme' && gameState.value.owned.includes(item.id))
  if (!ownedThemes.length) return
  const currentIndex = ownedThemes.findIndex((item) => item.id === gameState.value.equippedTheme)
  const nextTheme = ownedThemes[(currentIndex + 1) % ownedThemes.length]
  gameState.value = equipItem(nextTheme.id)
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  --page-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --soft-panel: rgba(255, 255, 255, 0.94);
  --accent: #667eea;
  --accent-2: #764ba2;
  --text-on-bg: white;
  --muted-on-bg: rgba(255, 255, 255, 0.8);
  background: var(--page-bg);
}

.home-container.theme-theme_cute {
  --page-bg:
    radial-gradient(circle at 16% 12%, rgba(255, 255, 255, .55), transparent 22%),
    linear-gradient(135deg, #ffaecb 0%, #93d8ff 100%);
  --accent: #f06292;
  --accent-2: #4fc3f7;
  --muted-on-bg: rgba(75, 55, 86, .72);
}

.home-container.theme-theme_cool {
  --page-bg:
    linear-gradient(rgba(5, 9, 20, .2), rgba(5, 9, 20, .35)),
    linear-gradient(135deg, #0b1020 0%, #2a1768 52%, #00bcd4 100%);
  --soft-panel: rgba(17, 25, 42, .92);
  --accent: #00d4ff;
  --accent-2: #7c4dff;
  --muted-on-bg: rgba(205, 244, 255, .78);
}

.home-container.theme-theme_plush {
  --page-bg:
    radial-gradient(circle at 22% 10%, rgba(255,255,255,.58), transparent 18%),
    linear-gradient(135deg, #e6a16f 0%, #f5d6b8 52%, #b97854 100%);
  --accent: #b97854;
  --accent-2: #7d4c3d;
  --muted-on-bg: rgba(75, 49, 41, .72);
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
  color: var(--text-on-bg);
  font-size: 24px;
  margin: 0;
}

.logo p {
  color: var(--muted-on-bg);
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

.study-desktop {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 28px;
  align-items: stretch;
  padding: 52px 0;
}

.desktop-main {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.desktop-eyebrow {
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
  margin: 0 0 12px;
}

.desktop-main h2 {
  color: var(--text-on-bg);
  font-size: 42px;
  margin-bottom: 16px;
}

.desktop-main p {
  color: var(--muted-on-bg);
  font-size: 18px;
  margin-bottom: 32px;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.desktop-card {
  padding: 28px;
  border-radius: 22px;
  background: var(--soft-panel);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
}

.plan-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #eef0f6;
}

.plan-row span {
  color: #888;
  font-size: 14px;
}

.plan-row strong {
  color: #333;
  text-align: right;
}

.plan-row.warning strong {
  color: #e65100;
}

.skill-reminders {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.skill-reminders button {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 4px 10px;
  align-items: center;
  min-height: 72px;
  padding: 12px;
  border: 1px solid #eef0f6;
  border-radius: 14px;
  background: #f8f9ff;
  color: #333;
  text-align: left;
  cursor: pointer;
  transition: all .2s;
}

.skill-reminders button:hover {
  transform: translateY(-2px);
  border-color: #dfe3ff;
  box-shadow: 0 10px 24px rgba(102, 126, 234, 0.14);
}

.skill-reminders span {
  grid-row: span 2;
  font-size: 24px;
}

.skill-reminders strong {
  font-size: 14px;
}

.skill-reminders small {
  color: #888;
  font-size: 12px;
}

.desktop-progress {
  height: 10px;
  margin: 22px 0 12px;
  overflow: hidden;
  border-radius: 999px;
  background: #eef0f6;
}

.desktop-progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
  transition: width 0.3s;
}

.desktop-card small {
  color: #999;
}

.companion-row {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 14px;
  align-items: center;
  margin: 18px 0 12px;
  padding: 14px;
  border-radius: 14px;
  background: #f8f9ff;
}

.desktop-pet {
  display: grid;
  place-items: center;
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: white;
  box-shadow: inset 0 0 0 1px #eceeff;
}

.companion-row strong {
  display: block;
  color: #4a3f70;
  font-size: 14px;
  margin-bottom: 4px;
}

.companion-row p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.55;
}

.btn-primary {
  background: white;
  color: var(--accent);
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
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 10%, white) 0%, color-mix(in srgb, var(--accent-2) 10%, white) 100%);
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

@media (max-width: 820px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav {
    flex-wrap: wrap;
  }

  .main-content {
    padding: 24px 16px;
  }

  .study-desktop {
    grid-template-columns: 1fr;
    padding: 34px 0;
  }

  .desktop-main h2 {
    font-size: 32px;
  }

  .plan-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .plan-row strong {
    text-align: left;
  }

  .skill-reminders {
    grid-template-columns: 1fr;
  }

  .level-cards {
    grid-template-columns: 1fr;
  }
}
</style>
