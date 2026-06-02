<template>
  <div class="pet-avatar" :class="[petId, size, mood]">
    <svg v-if="petId === 'pet_lamp'" viewBox="0 0 160 160" role="img" aria-label="台灯学长">
      <ellipse class="shadow" cx="80" cy="143" rx="46" ry="10" />
      <path class="ear left" d="M46 45 C34 27 43 17 58 32" />
      <path class="ear right" d="M114 45 C126 27 117 17 102 32" />
      <path class="body lamp-body" d="M38 74 C38 43 56 27 80 27 C104 27 122 43 122 74 C122 111 104 134 80 134 C56 134 38 111 38 74Z" />
      <path class="lamp-glow" d="M54 57 C60 42 70 36 80 36 C96 36 106 49 109 67 C92 60 71 60 54 57Z" />
      <circle class="cheek" cx="58" cy="86" r="7" />
      <circle class="cheek" cx="102" cy="86" r="7" />
      <circle class="eye" cx="65" cy="76" r="5" />
      <circle class="eye" cx="95" cy="76" r="5" />
      <path class="mouth" d="M72 93 Q80 101 88 93" />
      <path class="paw left-paw" d="M47 105 Q36 112 42 123 Q55 121 58 109" />
      <path class="paw right-paw" d="M113 105 Q124 112 118 123 Q105 121 102 109" />
    </svg>

    <svg v-else-if="petId === 'pet_cloud'" viewBox="0 0 160 160" role="img" aria-label="白噪音云">
      <ellipse class="shadow" cx="80" cy="143" rx="50" ry="10" />
      <path class="body cloud-body" d="M42 100 C25 99 20 78 34 67 C35 47 55 39 69 50 C79 31 110 36 114 59 C134 60 143 81 131 96 C123 111 55 113 42 100Z" />
      <circle class="fluff" cx="52" cy="76" r="22" />
      <circle class="fluff" cx="80" cy="65" r="28" />
      <circle class="fluff" cx="108" cy="78" r="23" />
      <circle class="cheek" cx="57" cy="90" r="6" />
      <circle class="cheek" cx="103" cy="90" r="6" />
      <circle class="eye" cx="66" cy="83" r="5" />
      <circle class="eye" cx="94" cy="83" r="5" />
      <path class="mouth" d="M73 98 Q80 104 87 98" />
      <path class="paw left-paw" d="M50 111 Q43 119 50 126" />
      <path class="paw right-paw" d="M110 111 Q117 119 110 126" />
    </svg>

    <svg v-else viewBox="0 0 160 160" role="img" aria-label="软绒小咖啡人">
      <ellipse class="shadow" cx="80" cy="143" rx="47" ry="10" />
      <path class="ear left" d="M46 48 C30 34 37 21 56 34" />
      <path class="ear right" d="M114 48 C130 34 123 21 104 34" />
      <path class="body coffee-body" d="M36 75 C36 43 57 28 80 28 C103 28 124 43 124 75 C124 112 103 135 80 135 C57 135 36 112 36 75Z" />
      <path class="cream" d="M51 55 C61 41 73 47 80 39 C91 50 105 39 113 58 C94 52 68 52 51 55Z" />
      <path class="handle" d="M121 75 C145 73 145 107 121 105" />
      <circle class="cheek" cx="58" cy="88" r="7" />
      <circle class="cheek" cx="102" cy="88" r="7" />
      <circle class="eye" cx="66" cy="78" r="5" />
      <circle class="eye" cx="94" cy="78" r="5" />
      <path class="mouth" d="M72 96 Q80 104 88 96" />
      <path class="paw left-paw" d="M47 107 Q35 114 42 125 Q56 122 58 110" />
      <path class="paw right-paw" d="M113 107 Q125 114 118 125 Q104 122 102 110" />
    </svg>
  </div>
</template>

<script setup>
defineProps({
  petId: {
    type: String,
    default: 'pet_coffee'
  },
  size: {
    type: String,
    default: 'medium'
  },
  mood: {
    type: String,
    default: 'idle'
  }
})
</script>

<style scoped>
.pet-avatar {
  display: grid;
  place-items: center;
  width: 120px;
  height: 120px;
}

.pet-avatar.small {
  width: 78px;
  height: 78px;
}

.pet-avatar.large {
  width: 170px;
  height: 170px;
}

svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.focusing svg {
  animation: soft-bob 2s ease-in-out infinite;
}

.resting svg {
  transform: rotate(-5deg);
  opacity: 0.82;
}

.encourage svg {
  animation: cheer-pulse 1.8s ease-in-out infinite;
}

.warning svg {
  animation: tiny-shake 0.42s ease-in-out 2;
}

.celebrate svg {
  animation: celebrate-pop 1.2s ease-in-out infinite;
}

.sleepy svg {
  transform: rotate(-8deg) translateY(6px);
  opacity: 0.72;
  filter: saturate(0.74);
}

.celebrate .cheek,
.encourage .cheek {
  fill: rgba(255, 118, 136, 0.82);
}

.warning .cheek {
  fill: rgba(255, 178, 80, 0.78);
}

.shadow {
  fill: rgba(31, 24, 36, 0.18);
}

.body,
.ear,
.paw,
.fluff {
  stroke: rgba(81, 54, 50, 0.28);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.coffee-body {
  fill: #b97854;
}

.lamp-body {
  fill: #f2c766;
}

.cloud-body,
.fluff {
  fill: #f7f4ee;
}

.ear,
.paw {
  fill: #c98b68;
}

.pet_lamp .ear,
.pet_lamp .paw {
  fill: #f5d57f;
}

.pet_cloud .paw {
  fill: #f7f4ee;
}

.cream,
.lamp-glow {
  fill: #fff3d7;
  stroke: rgba(81, 54, 50, 0.18);
  stroke-width: 2;
}

.handle {
  fill: none;
  stroke: #9f6649;
  stroke-width: 11;
  stroke-linecap: round;
}

.eye {
  fill: #3a2a28;
}

.cheek {
  fill: rgba(255, 148, 142, 0.55);
}

.mouth {
  fill: none;
  stroke: #3a2a28;
  stroke-width: 3;
  stroke-linecap: round;
}

@keyframes soft-bob {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes cheer-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.045) translateY(-2px);
  }
}

@keyframes tiny-shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-3px);
  }
  75% {
    transform: translateX(3px);
  }
}

@keyframes celebrate-pop {
  0%, 100% {
    transform: translateY(0) rotate(0);
  }
  35% {
    transform: translateY(-8px) rotate(-3deg);
  }
  70% {
    transform: translateY(-3px) rotate(3deg);
  }
}
</style>
