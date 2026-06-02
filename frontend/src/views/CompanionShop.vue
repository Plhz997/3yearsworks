<template>
  <div class="shop-container">
    <header class="shop-header">
      <div>
        <h2>咖啡豆商店</h2>
        <p>用专注获得的咖啡豆和能量，兑换宠物、头像框、壁纸和界面皮肤。</p>
      </div>
      <button @click="goBack">返回</button>
    </header>

    <section class="wallet-card">
      <div><span>咖啡豆</span><strong>{{ gameState.coffeeBeans }}</strong></div>
      <div><span>能量值</span><strong>{{ gameState.energyValue }}</strong></div>
      <div><span>今日专注</span><strong>{{ gameState.todayFocusCount }}</strong></div>
      <div><span>连续天数</span><strong>{{ gameState.streakDays }}</strong></div>
    </section>

    <nav class="category-tabs">
      <button v-for="category in categories" :key="category.id" :class="{ active: activeCategory === category.id }" @click="activeCategory = category.id">
        {{ category.label }}
      </button>
    </nav>

    <section class="shop-grid">
      <article v-for="item in filteredItems" :key="item.id" class="shop-item" :class="item.rarity">
        <div class="item-icon" :class="item.type === 'theme' ? `preview-${item.id}` : ''">
          <PetAvatar v-if="item.type === 'pet'" :pet-id="item.id" size="small" />
          <span v-else>{{ item.icon }}</span>
        </div>
        <div class="item-body">
          <div class="item-title">
            <h3>{{ item.name }}</h3>
            <span>{{ rarityLabel(item.rarity) }}</span>
          </div>
          <p>{{ item.description }}</p>
          <div class="price-row">
            <b>☕ {{ item.priceBeans }}</b>
            <b v-if="item.priceEnergy">⚡ {{ item.priceEnergy }}</b>
          </div>
        </div>
        <button v-if="canEquip(item)" @click="equip(item.id)">
          {{ equippedText(item) }}
        </button>
        <button v-else @click="buy(item.id)">
          {{ ownedText(item) }}
        </button>
      </article>
    </section>

    <div v-if="message" class="toast">{{ message }}</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import PetAvatar from '../components/PetAvatar.vue'
import { equipItem, loadGameState, purchaseItem, shopCatalog } from '../utils/gamification'

const router = useRouter()
const gameState = ref(loadGameState())
const activeCategory = ref('all')
const message = ref('')
const categories = [
  { id: 'all', label: '全部' },
  { id: 'pet', label: '宠物' },
  { id: 'frame', label: '头像框' },
  { id: 'wallpaper', label: '壁纸' },
  { id: 'theme', label: '皮肤' },
  { id: 'boost', label: '道具' }
]

const filteredItems = computed(() => {
  if (activeCategory.value === 'all') return shopCatalog
  return shopCatalog.filter((item) => item.type === activeCategory.value)
})

const goBack = () => {
  router.push('/profile')
}

const buy = (itemId) => {
  const result = purchaseItem(itemId)
  gameState.value = result.state
  showMessage(result.message)
}

const equip = (itemId) => {
  gameState.value = equipItem(itemId)
  showMessage('已装备')
}

const showMessage = (text) => {
  message.value = text
  setTimeout(() => {
    message.value = ''
  }, 2200)
}

const canEquip = (item) => gameState.value.owned.includes(item.id) && item.type !== 'boost'

const ownedText = (item) => {
  if (gameState.value.owned.includes(item.id) && item.type !== 'boost') return '已拥有'
  return '兑换'
}

const equippedText = (item) => {
  if (
    item.id === gameState.value.equippedPet ||
    item.id === gameState.value.equippedFrame ||
    item.id === gameState.value.equippedWallpaper ||
    item.id === gameState.value.equippedTheme
  ) {
    return '使用中'
  }
  return '装备'
}

const rarityLabel = (rarity) => ({
  starter: '初始',
  common: '普通',
  rare: '稀有',
  epic: '史诗'
}[rarity] || '普通')
</script>

<style scoped>
.shop-container {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.shop-header,
.wallet-card,
.category-tabs,
.shop-grid {
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 22px;
  color: white;
}

.shop-header h2 {
  margin: 0 0 8px;
  font-size: 32px;
}

.shop-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
}

.shop-header button,
.category-tabs button,
.shop-item button {
  min-height: 40px;
  padding: 0 18px;
  border: none;
  border-radius: 20px;
  font-weight: 700;
  cursor: pointer;
}

.shop-header button {
  background: white;
  color: #667eea;
}

.wallet-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.wallet-card div {
  padding: 18px;
  border-radius: 16px;
  background: white;
  text-align: center;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
}

.wallet-card span {
  display: block;
  color: #999;
  font-size: 13px;
}

.wallet-card strong {
  display: block;
  margin-top: 8px;
  color: #333;
  font-size: 28px;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.category-tabs button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.category-tabs button.active {
  background: white;
  color: #667eea;
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.shop-item {
  display: grid;
  grid-template-columns: 78px 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 20px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.12);
}

.shop-item.rare {
  box-shadow: 0 8px 28px rgba(33, 150, 243, 0.28);
}

.shop-item.epic {
  box-shadow: 0 8px 28px rgba(156, 39, 176, 0.28);
}

.item-icon {
  display: grid;
  place-items: center;
  width: 70px;
  height: 70px;
  border-radius: 18px;
  background: #f5f7ff;
  font-size: 34px;
  overflow: visible;
}

.item-icon.preview-theme_classic {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.item-icon.preview-theme_cute {
  background: linear-gradient(135deg, #ffd6e7 0%, #b7e7ff 100%);
  color: #9b4f7a;
}

.item-icon.preview-theme_cool {
  background: linear-gradient(135deg, #101827 0%, #2c1b68 55%, #00d4ff 100%);
  color: #8ff6ff;
}

.item-icon.preview-theme_plush {
  background:
    radial-gradient(circle at 28% 24%, rgba(255,255,255,.8), transparent 24%),
    linear-gradient(135deg, #f4c89b 0%, #d99b7d 100%);
  color: #7a4f3f;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-title h3 {
  margin: 0;
  color: #333;
}

.item-title span {
  padding: 4px 10px;
  border-radius: 12px;
  background: #f5f7fa;
  color: #667eea;
  font-size: 12px;
}

.item-body p {
  margin: 8px 0 10px;
  color: #666;
  line-height: 1.6;
}

.price-row {
  display: flex;
  gap: 12px;
  color: #333;
}

.shop-item button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  padding: 12px 18px;
  border-radius: 22px;
  background: #333;
  color: white;
  font-weight: 700;
}

@media (max-width: 760px) {
  .shop-header,
  .shop-item {
    grid-template-columns: 1fr;
  }

  .shop-header {
    align-items: flex-start;
  }

  .wallet-card,
  .shop-grid {
    grid-template-columns: 1fr;
  }
}
</style>
