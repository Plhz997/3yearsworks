const STORAGE_KEY = 'word-companion-game'

export const shopCatalog = [
  {
    id: 'pet_coffee',
    type: 'pet',
    name: '小咖啡人',
    icon: '☕',
    priceBeans: 30,
    priceEnergy: 0,
    rarity: 'starter',
    description: '专注时坐在桌边陪你复习错词。'
  },
  {
    id: 'pet_lamp',
    type: 'pet',
    name: '台灯学长',
    icon: '💡',
    priceBeans: 55,
    priceEnergy: 20,
    rarity: 'rare',
    description: '深夜学习时给你稳定的光。'
  },
  {
    id: 'pet_cloud',
    type: 'pet',
    name: '白噪音云',
    icon: '☁️',
    priceBeans: 75,
    priceEnergy: 45,
    rarity: 'epic',
    description: '把杂念隔在云层外面。'
  },
  {
    id: 'frame_library',
    type: 'frame',
    name: '图书馆木纹框',
    icon: '▧',
    priceBeans: 25,
    priceEnergy: 10,
    rarity: 'common',
    description: '安静耐看的个人头像框。'
  },
  {
    id: 'frame_neon',
    type: 'frame',
    name: '雨夜霓虹框',
    icon: '◇',
    priceBeans: 48,
    priceEnergy: 22,
    rarity: 'rare',
    description: '带一点雨夜咖啡馆的亮色。'
  },
  {
    id: 'wallpaper_cafe',
    type: 'wallpaper',
    name: '雨夜咖啡馆壁纸',
    icon: '🌧️',
    priceBeans: 40,
    priceEnergy: 12,
    rarity: 'common',
    description: '个人主页背景换成暖色雨夜。'
  },
  {
    id: 'wallpaper_morning',
    type: 'wallpaper',
    name: '晨间自习室壁纸',
    icon: '🌤️',
    priceBeans: 50,
    priceEnergy: 25,
    rarity: 'rare',
    description: '清爽明亮的晨间主页背景。'
  },
  {
    id: 'theme_classic',
    type: 'theme',
    name: '经典紫藤风',
    icon: '✦',
    priceBeans: 0,
    priceEnergy: 0,
    rarity: 'starter',
    description: '保留原来词汇测评的紫色渐变界面。'
  },
  {
    id: 'theme_cute',
    type: 'theme',
    name: '可爱奶糖风',
    icon: '♡',
    priceBeans: 35,
    priceEnergy: 20,
    rarity: 'common',
    description: '柔和粉蓝配色，适合轻松背词和陪学。'
  },
  {
    id: 'theme_cool',
    type: 'theme',
    name: '炫酷霓虹风',
    icon: '◇',
    priceBeans: 60,
    priceEnergy: 45,
    rarity: 'rare',
    description: '深色霓虹界面，适合夜间刷题和精听。'
  },
  {
    id: 'theme_plush',
    type: 'theme',
    name: '玩偶绒绒风',
    icon: '◌',
    priceBeans: 80,
    priceEnergy: 65,
    rarity: 'epic',
    description: '像小玩偶学习桌一样柔软，咖啡人更有陪伴感。'
  },
  {
    id: 'boost_focus',
    type: 'boost',
    name: '轻量任务券',
    icon: '🎟️',
    priceBeans: 18,
    priceEnergy: 0,
    rarity: 'common',
    description: '中断后快速开启 10 分钟轻量任务。'
  }
]

const defaultState = {
  coffeeBeans: 0,
  energyValue: 0,
  todayDate: '',
  todayFocusCount: 0,
  todayInterruptions: 0,
  totalFocusCount: 0,
  streakDays: 0,
  lastFocusDate: '',
  owned: ['pet_coffee', 'theme_classic'],
  equippedPet: 'pet_coffee',
  equippedFrame: '',
  equippedWallpaper: '',
  equippedTheme: 'theme_classic',
  inventory: {
    boost_focus: 0
  }
}

export const loadGameState = () => {
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  const today = new Date().toISOString().slice(0, 10)
  const merged = {
    ...defaultState,
    ...stored,
    inventory: {
      ...defaultState.inventory,
      ...(stored.inventory || {})
    }
  }
  if (merged.todayDate !== today) {
    merged.todayDate = today
    merged.todayFocusCount = 0
    merged.todayInterruptions = 0
  }
  saveGameState(merged)
  return merged
}

export const saveGameState = (state) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export const addRewards = ({ beans = 0, energy = 0 }) => {
  const state = loadGameState()
  state.coffeeBeans += beans
  state.energyValue += energy
  saveGameState(state)
  return state
}

export const addFocusSession = () => {
  const state = loadGameState()
  const today = new Date().toISOString().slice(0, 10)
  state.todayDate = today
  state.todayFocusCount += 1
  state.totalFocusCount += 1
  if (state.lastFocusDate !== today) {
    state.streakDays = state.lastFocusDate ? state.streakDays + 1 : 1
    state.lastFocusDate = today
  }
  saveGameState(state)
  return state
}

export const addInterruption = () => {
  const state = loadGameState()
  state.todayInterruptions = (state.todayInterruptions || 0) + 1
  saveGameState(state)
  return state
}

export const companionStates = {
  idle: {
    mood: 'idle',
    label: '等待中',
    message: '今天也一起学 25 分钟吧。'
  },
  focus: {
    mood: 'focusing',
    label: '陪学中',
    message: '我也在学习，先不要退出。'
  },
  break: {
    mood: 'resting',
    label: '休息中',
    message: '我也休息一下，回来继续陪你看单词。'
  },
  encourage: {
    mood: 'encourage',
    label: '鼓励',
    message: '错词有点多，我给你递来一张复习卡。'
  },
  warning: {
    mood: 'warning',
    label: '提醒',
    message: '今天中断有点多，要不要改成 10 分钟轻量任务？'
  },
  celebrate: {
    mood: 'celebrate',
    label: '庆祝',
    message: '这轮完成了，错词我已经帮你放进复习篮了。'
  },
  sleepy: {
    mood: 'sleepy',
    label: '困倦',
    message: '我有点困了，等你回来开一轮轻量复习。'
  }
}

const daysBetween = (fromDate, toDate) => {
  if (!fromDate || !toDate) return 0
  const from = new Date(`${fromDate}T00:00:00`)
  const to = new Date(`${toDate}T00:00:00`)
  return Math.floor((to - from) / 86400000)
}

export const resolveCompanionState = ({
  phase = 'idle',
  running = false,
  completed = false,
  report = null,
  wrongCount = 0,
  gameState = loadGameState()
} = {}) => {
  const today = new Date().toISOString().slice(0, 10)
  let stateId = 'idle'

  if (completed || report) stateId = 'celebrate'
  else if (phase === 'break') stateId = 'break'
  else if ((gameState.todayInterruptions || 0) >= 2) stateId = 'warning'
  else if (wrongCount > 10) stateId = 'encourage'
  else if (phase === 'focus' && running) stateId = 'focus'
  else if (gameState.streakDays >= 3 && gameState.todayFocusCount > 0) stateId = 'celebrate'
  else if (daysBetween(gameState.lastFocusDate, today) >= 3) stateId = 'sleepy'
  else stateId = 'idle'

  const base = companionStates[stateId]
  if (stateId === 'celebrate' && gameState.streakDays >= 3 && !completed && !report) {
    return {
      id: stateId,
      ...base,
      message: `连续专注 ${gameState.streakDays} 天了，我今天特别开心。`
    }
  }
  if (stateId === 'idle' && gameState.todayFocusCount === 0) {
    return {
      id: stateId,
      ...base,
      message: '今日番茄钟还没开始，我在桌边等你。'
    }
  }
  return { id: stateId, ...base }
}

export const purchaseItem = (itemId) => {
  const state = loadGameState()
  const item = shopCatalog.find((entry) => entry.id === itemId)
  if (!item) return { success: false, message: '商品不存在', state }
  if (state.owned.includes(itemId) && item.type !== 'boost') {
    return { success: false, message: '已经拥有这个物品', state }
  }
  if (state.coffeeBeans < item.priceBeans || state.energyValue < item.priceEnergy) {
    return { success: false, message: '咖啡豆或能量值不足', state }
  }
  state.coffeeBeans -= item.priceBeans
  state.energyValue -= item.priceEnergy
  if (item.type === 'boost') {
    state.inventory[item.id] = (state.inventory[item.id] || 0) + 1
  } else {
    state.owned.push(item.id)
  }
  saveGameState(state)
  return { success: true, message: `已兑换 ${item.name}`, state }
}

export const equipItem = (itemId) => {
  const state = loadGameState()
  const item = shopCatalog.find((entry) => entry.id === itemId)
  if (!item) return state
  if (!state.owned.includes(itemId)) return state
  if (item.type === 'pet') state.equippedPet = itemId
  if (item.type === 'frame') state.equippedFrame = itemId
  if (item.type === 'wallpaper') state.equippedWallpaper = itemId
  if (item.type === 'theme') state.equippedTheme = itemId
  saveGameState(state)
  return state
}

export const getCatalogItem = (itemId) => shopCatalog.find((item) => item.id === itemId)
