<template>
  <div class="profile-container" :class="[wallpaperClass, themeClass]">
    <DraggablePet
      :pet-id="gameState.equippedPet"
      :message="petMessage"
      :mood="companionState.mood"
      storage-key="profile-floating-pet"
      :initial-x="32"
      :initial-y="420"
    />
    <div class="header">
      <h2>个人主页</h2>
      <button @click="goBack" class="btn-back">返回</button>
    </div>

    <section class="hero-card">
      <div class="user-info">
        <div class="avatar" :class="frameClass">
          <PetAvatar :pet-id="gameState.equippedPet" size="small" />
        </div>
        <div class="user-details">
          <h3>{{ user?.username || '学习者' }}</h3>
          <p>{{ user?.email || '暂无邮箱' }}</p>
          <p class="join-date">注册于 {{ user?.created_at || '-' }}</p>
        </div>
      </div>
      <div class="pet-panel">
        <PetAvatar :pet-id="gameState.equippedPet" size="medium" :mood="companionState.mood" />
        <div>
          <strong>{{ equippedPet?.name || '小咖啡人' }}</strong>
          <span class="state-chip">{{ companionState.label }}</span>
          <p>{{ petMessage }}</p>
        </div>
      </div>
    </section>

    <section class="growth-card">
      <h3>伴学成长</h3>
      <div class="growth-grid">
        <div><span>咖啡豆</span><strong>{{ gameState.coffeeBeans }}</strong></div>
        <div><span>能量值</span><strong>{{ gameState.energyValue }}</strong></div>
        <div><span>今日专注</span><strong>{{ gameState.todayFocusCount }}</strong></div>
        <div><span>累计番茄</span><strong>{{ gameState.totalFocusCount }}</strong></div>
        <div><span>连续天数</span><strong>{{ gameState.streakDays }}</strong></div>
        <div><span>轻量任务券</span><strong>{{ gameState.inventory?.boost_focus || 0 }}</strong></div>
      </div>
    </section>

    <div class="stats-card">
      <h3>学习统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_tests || 0 }}</span>
            <span class="stat-label">测评次数</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">📊</div>
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

    <section class="collection-card">
      <h3>我的装扮</h3>
      <div class="collection-grid">
        <div>
          <span>当前宠物</span>
          <strong>{{ equippedPet?.name || '小咖啡人' }}</strong>
        </div>
        <div>
          <span>头像框</span>
          <strong>{{ equippedFrame?.name || '未装备' }}</strong>
        </div>
        <div>
          <span>壁纸</span>
          <strong>{{ equippedWallpaper?.name || '默认主页' }}</strong>
        </div>
        <div>
          <span>界面皮肤</span>
          <strong>{{ equippedTheme?.name || '经典紫藤风' }}</strong>
        </div>
      </div>
    </section>

    <div class="menu-card">
      <h3>功能菜单</h3>
      <div class="menu-items">
        <button @click="goTo('/pomodoro')" class="menu-item">
          <span class="menu-icon">🍅</span>
          <span>番茄伴学</span>
          <span class="menu-arrow">→</span>
        </button>
        <button @click="goTo('/companion-shop')" class="menu-item">
          <span class="menu-icon">☕</span>
          <span>咖啡豆商店</span>
          <span class="menu-arrow">→</span>
        </button>
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
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DraggablePet from '../components/DraggablePet.vue'
import PetAvatar from '../components/PetAvatar.vue'
import { authAPI, userAPI } from '../utils/api'
import { getCatalogItem, loadGameState, resolveCompanionState } from '../utils/gamification'

const router = useRouter()
const user = ref(null)
const gameState = ref(loadGameState())
const wrongWordCount = ref(0)
const stats = ref({
  total_tests: 0,
  avg_accuracy: 0,
  last_test_date: null
})

const equippedPet = computed(() => getCatalogItem(gameState.value.equippedPet))
const equippedFrame = computed(() => getCatalogItem(gameState.value.equippedFrame))
const equippedWallpaper = computed(() => getCatalogItem(gameState.value.equippedWallpaper))
const equippedTheme = computed(() => getCatalogItem(gameState.value.equippedTheme))
const frameClass = computed(() => gameState.value.equippedFrame ? `frame-${gameState.value.equippedFrame}` : '')
const wallpaperClass = computed(() => gameState.value.equippedWallpaper ? `wallpaper-${gameState.value.equippedWallpaper}` : '')
const themeClass = computed(() => `theme-${gameState.value.equippedTheme || 'theme_classic'}`)
const companionState = computed(() => {
  if (gameState.value.coffeeBeans >= 50 && (gameState.value.todayInterruptions || 0) < 2 && wrongWordCount.value <= 10) {
    return {
      id: 'celebrate',
      mood: 'celebrate',
      label: '想换装',
      message: '咖啡豆够多了，可以去商店看看新装扮。'
    }
  }
  return resolveCompanionState({
    wrongCount: wrongWordCount.value,
    gameState: gameState.value
  })
})
const petMessage = computed(() => companionState.value.message)

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    router.push('/login')
    return
  }

  try {
    const [userRes, statsRes, wrongRes] = await Promise.all([
      authAPI.profile(),
      userAPI.stats(),
      userAPI.wrongWords()
    ])

    if (userRes.data.success) user.value = userRes.data.user
    if (statsRes.data.success) stats.value = statsRes.data.stats
    if (wrongRes.data.success) {
      const words = wrongRes.data.wrong_words || wrongRes.data.data || []
      wrongWordCount.value = words.length
    }
  } catch (error) {
    console.error('获取数据失败', error)
  }
})

const goBack = () => {
  router.push('/')
}

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  if (!confirm('确定要退出登录吗？')) return
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 0%, rgba(102, 126, 234, 0.18), transparent 28%),
    #f5f7fa;
  padding: 40px 20px;
}

.profile-container.wallpaper-wallpaper_cafe {
  background:
    radial-gradient(circle at 80% 12%, rgba(255, 193, 107, 0.28), transparent 24%),
    linear-gradient(135deg, #f5f7fa 0%, #fff3ed 100%);
}

.profile-container.wallpaper-wallpaper_morning {
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 235, 150, 0.32), transparent 24%),
    linear-gradient(135deg, #f5fbff 0%, #effbea 100%);
}

.profile-container.theme-theme_cute {
  background:
    radial-gradient(circle at 18% 10%, rgba(255,255,255,.6), transparent 22%),
    linear-gradient(135deg, #fff0f7 0%, #e4f7ff 100%);
}

.profile-container.theme-theme_cool {
  background:
    radial-gradient(circle at 82% 8%, rgba(0,212,255,.2), transparent 24%),
    linear-gradient(135deg, #101827 0%, #21144e 100%);
}

.profile-container.theme-theme_cool .header h2 {
  color: white;
}

.profile-container.theme-theme_plush {
  background:
    radial-gradient(circle at 20% 0%, rgba(255,255,255,.5), transparent 22%),
    linear-gradient(135deg, #fff4ea 0%, #f3d0b7 100%);
}

.header,
.hero-card,
.growth-card,
.stats-card,
.collection-card,
.menu-card,
.action-card {
  max-width: 920px;
  margin: 0 auto 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  color: #333;
  font-size: 28px;
}

.btn-back {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
}

.hero-card,
.growth-card,
.stats-card,
.collection-card,
.menu-card,
.action-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.hero-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 20px;
  align-items: center;
}

.user-info,
.pet-panel {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  display: grid;
  place-items: center;
  width: 104px;
  height: 104px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: visible;
}

.avatar.frame-frame_library {
  border: 5px solid #8d6e63;
}

.avatar.frame-frame_neon {
  border: 5px solid #7c4dff;
  box-shadow: 0 0 24px rgba(124, 77, 255, 0.45);
}

.user-details h3,
.growth-card h3,
.stats-card h3,
.collection-card h3,
.menu-card h3 {
  margin: 0 0 16px;
  color: #333;
}

.user-details p {
  margin: 0 0 4px;
  color: #666;
}

.join-date {
  color: #999 !important;
  font-size: 12px;
}

.pet-panel {
  padding: 18px;
  border-radius: 16px;
  background: #f8f9ff;
}

.pet-panel strong {
  color: #333;
}

.state-chip {
  display: inline-block;
  margin-left: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #eef2ff;
  color: #667eea;
  font-size: 12px;
  font-weight: 800;
  vertical-align: middle;
}

.pet-panel p {
  margin: 8px 0 0;
  color: #666;
  line-height: 1.6;
}

.growth-grid,
.collection-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.growth-grid div,
.collection-grid div,
.stat-item {
  padding: 16px;
  border-radius: 12px;
  background: #f8f9fa;
  text-align: center;
}

.growth-grid span,
.collection-grid span,
.stat-label {
  display: block;
  color: #999;
  font-size: 12px;
}

.growth-grid strong,
.collection-grid strong,
.stat-value {
  display: block;
  margin-top: 8px;
  color: #333;
  font-size: 20px;
  font-weight: 700;
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.menu-icon {
  font-size: 20px;
}

.menu-item span:nth-child(2) {
  flex: 1;
  text-align: left;
  padding-left: 16px;
  color: #333;
  font-size: 16px;
}

.menu-arrow {
  color: #999;
}

.action-card {
  text-align: center;
}

.logout-btn {
  width: 100%;
  padding: 14px;
  background: #ffebee;
  color: #f44336;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 760px) {
  .hero-card,
  .growth-grid,
  .collection-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
