import { ref, watch } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'classic')

export const themes = [
  { id: 'classic', name: '经典蓝紫', icon: '💜', color: '#667eea' },
  { id: 'forest', name: '自然森林', icon: '🌿', color: '#11998e' },
  { id: 'sunset', name: '日落暖橙', icon: '🌅', color: '#f12711' },
  { id: 'midnight', name: '暗夜模式', icon: '🌙', color: '#bb86fc' },
  { id: 'sakura', name: '梦幻樱花', icon: '🌸', color: '#f093fb' },
  { id: 'ocean', name: '深邃海洋', icon: '🌊', color: '#0077b6' },
]

export function useTheme() {
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const initTheme = () => {
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  return { theme, setTheme, initTheme, themes }
}