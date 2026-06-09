<template>
  <div class="theme-switcher">
    <button class="theme-toggle-btn" @click="showPicker = !showPicker" title="切换皮肤">
      <span class="current-icon">{{ currentTheme?.icon || '🎨' }}</span>
      <span class="current-name">{{ currentTheme?.name || '皮肤' }}</span>
    </button>

    <div v-if="showPicker" class="theme-picker" @click.self="showPicker = false">
      <div class="theme-picker-header">
        <h4>选择皮肤</h4>
        <button class="close-btn" @click="showPicker = false">✕</button>
      </div>
      <div class="theme-list">
        <div
          v-for="t in themes"
          :key="t.id"
          class="theme-item"
          :class="{ active: theme === t.id }"
          @click="selectTheme(t.id)"
        >
          <div class="theme-preview" :style="{ background: t.color }">
            <span class="theme-icon">{{ t.icon }}</span>
          </div>
          <div class="theme-info">
            <span class="theme-name">{{ t.name }}</span>
            <span v-if="theme === t.id" class="check-mark">✓</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTheme } from '../composables/useTheme'

const { theme, setTheme, themes } = useTheme()
const showPicker = ref(false)

const currentTheme = computed(() => themes.find(t => t.id === theme.value))

const selectTheme = (id) => {
  setTheme(id)
  showPicker.value = false
}
</script>

<style scoped>
.theme-switcher {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 24px;
  cursor: pointer;
  box-shadow: var(--shadow);
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.current-icon {
  font-size: 18px;
}

.current-name {
  font-weight: 500;
}

.theme-picker {
  position: absolute;
  bottom: 60px;
  right: 0;
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: var(--shadow-hover);
  width: 280px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.theme-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.theme-picker-header h4 {
  font-size: 16px;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: var(--btn-secondary-bg);
}

.theme-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theme-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-item:hover {
  background: var(--btn-secondary-bg);
}

.theme-item.active {
  background: var(--btn-secondary-bg);
  outline: 2px solid var(--accent-primary);
  outline-offset: -2px;
}

.theme-preview {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.theme-icon {
  font-size: 20px;
}

.theme-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.theme-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.check-mark {
  color: var(--accent-primary);
  font-weight: bold;
  font-size: 16px;
}
</style>