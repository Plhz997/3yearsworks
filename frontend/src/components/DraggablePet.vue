<template>
  <div
    class="draggable-pet"
    :class="[mood, { dragging, collapsed }]"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @pointerdown="startDrag"
  >
    <button class="collapse-btn" @click.stop="collapsed = !collapsed">{{ collapsed ? '展开' : '收起' }}</button>
    <div v-if="!collapsed" class="bubble">{{ message }}</div>
    <PetAvatar :pet-id="petId" size="large" :mood="mood" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import PetAvatar from './PetAvatar.vue'

const props = defineProps({
  petId: {
    type: String,
    default: 'pet_coffee'
  },
  mood: {
    type: String,
    default: 'idle'
  },
  message: {
    type: String,
    default: '今天也一起学一会儿吧。'
  },
  storageKey: {
    type: String,
    default: 'draggable-study-pet'
  },
  initialX: {
    type: Number,
    default: 28
  },
  initialY: {
    type: Number,
    default: 360
  }
})

const position = reactive({ x: props.initialX, y: props.initialY })
const dragging = ref(false)
const collapsed = ref(false)
let startX = 0
let startY = 0
let originX = 0
let originY = 0

onMounted(() => {
  const saved = JSON.parse(localStorage.getItem(props.storageKey) || 'null')
  if (saved) {
    position.x = saved.x
    position.y = saved.y
  } else {
    clampPosition()
  }
})

const startDrag = (event) => {
  dragging.value = true
  startX = event.clientX
  startY = event.clientY
  originX = position.x
  originY = position.y
  event.currentTarget.setPointerCapture(event.pointerId)
  window.addEventListener('pointermove', moveDrag)
  window.addEventListener('pointerup', stopDrag, { once: true })
}

const moveDrag = (event) => {
  if (!dragging.value) return
  position.x = originX + event.clientX - startX
  position.y = originY + event.clientY - startY
  clampPosition()
}

const stopDrag = () => {
  dragging.value = false
  clampPosition()
  localStorage.setItem(props.storageKey, JSON.stringify({ x: position.x, y: position.y }))
  window.removeEventListener('pointermove', moveDrag)
}

const clampPosition = () => {
  const width = collapsed.value ? 120 : 230
  const height = collapsed.value ? 130 : 230
  position.x = Math.max(8, Math.min(position.x, window.innerWidth - width))
  position.y = Math.max(8, Math.min(position.y, window.innerHeight - height))
}
</script>

<style scoped>
.draggable-pet {
  position: fixed;
  z-index: 80;
  display: grid;
  justify-items: center;
  gap: 8px;
  width: 230px;
  user-select: none;
  touch-action: none;
  cursor: grab;
}

.draggable-pet.dragging {
  cursor: grabbing;
}

.draggable-pet.collapsed {
  width: 120px;
}

.draggable-pet.warning .bubble {
  background: rgba(255, 247, 230, 0.96);
  color: #7a3f00;
  box-shadow: 0 12px 36px rgba(255, 152, 0, 0.2);
}

.draggable-pet.warning .bubble::after {
  background: rgba(255, 247, 230, 0.96);
}

.draggable-pet.celebrate .bubble,
.draggable-pet.encourage .bubble {
  background: rgba(244, 255, 247, 0.96);
  color: #255b3b;
  box-shadow: 0 12px 36px rgba(67, 160, 71, 0.2);
}

.draggable-pet.celebrate .bubble::after,
.draggable-pet.encourage .bubble::after {
  background: rgba(244, 255, 247, 0.96);
}

.draggable-pet.sleepy .bubble {
  background: rgba(242, 240, 255, 0.96);
  color: #51456d;
}

.draggable-pet.sleepy .bubble::after {
  background: rgba(242, 240, 255, 0.96);
}

.bubble {
  max-width: 220px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  color: #3b2f2f;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.5;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.16);
}

.bubble::after {
  content: "";
  display: block;
  width: 14px;
  height: 14px;
  margin: 6px auto -19px;
  background: rgba(255, 255, 255, 0.95);
  transform: rotate(45deg);
}

.collapse-btn {
  justify-self: end;
  min-height: 28px;
  padding: 0 10px;
  border: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.76);
  color: #59433d;
  font-size: 12px;
  font-weight: 800;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12);
}

@media (max-width: 640px) {
  .draggable-pet {
    width: 180px;
  }

  .bubble {
    max-width: 178px;
    font-size: 13px;
  }
}
</style>
