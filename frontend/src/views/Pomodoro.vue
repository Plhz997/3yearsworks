<template>
  <div class="pomodoro-page" :class="[selectedScene.id, { break: phase === 'break', active: sessionStarted }]">
    <button class="exit-btn" @click="handleExit">{{ sessionStarted ? '退出伴学' : '返回首页' }}</button>
    <DraggablePet
      v-if="sessionStarted"
      :pet-id="selectedScene.petId"
      :message="roleMessage"
      :mood="companionState.mood"
      storage-key="pomodoro-floating-pet"
      :initial-x="32"
      :initial-y="320"
    />

    <main v-if="!sessionStarted && !report" class="task-setup">
      <p class="eyebrow">STUDY POMODORO</p>
      <h1>选择学习场景和专注任务</h1>
      <p class="setup-desc">开始后进入虚拟咖啡馆专注舱，背单词、阅读、精听和跟读都可以在这里完成。</p>

      <section class="scene-grid">
        <button
          v-for="scene in scenes"
          :key="scene.id"
          :class="['scene-card', scene.id, { active: selectedSceneId === scene.id }]"
          @click="selectScene(scene.id)"
        >
          <span>{{ scene.name }}</span>
          <strong>{{ scene.role }}</strong>
          <small>{{ scene.noiseLabel }} · {{ scene.mood }}</small>
        </button>
      </section>

      <section v-if="selectedTask.usesWords" class="group-grid">
        <button
          v-for="group in wordGroups"
          :key="group.id"
          :class="['group-card', { active: selectedGroupId === group.id }]"
          @click="selectGroup(group.id)"
        >
          <strong>{{ group.name }}</strong>
          <small>{{ group.desc }}</small>
        </button>
      </section>

      <section class="task-grid">
        <button
          v-for="task in taskTemplates"
          :key="task.id"
          :class="['task-card', { active: selectedTaskId === task.id }]"
          @click="selectTask(task.id)"
        >
          <span>{{ task.icon }}</span>
          <strong>{{ task.title }}</strong>
          <small>{{ task.description }}</small>
        </button>
      </section>

      <section class="setup-panel">
        <label>
          <span>今日任务</span>
          <input v-model.trim="taskTitle" type="text" placeholder="例如：复习四级核心词 Unit 3" />
        </label>
        <label v-if="!selectedTask.usesWords">
          <span>学习水平</span>
          <select v-model="studyLevel">
            <option>初中</option>
            <option>高中</option>
            <option>四级</option>
            <option>六级</option>
          </select>
          <b>AI 匹配</b>
        </label>
        <label v-if="!selectedTask.usesWords">
          <span>主题偏好</span>
          <input v-model.trim="studyTopic" type="text" placeholder="例如：校园生活、科技、环保" />
        </label>
        <label v-if="!selectedTask.usesWords">
          <span>薄弱点</span>
          <input v-model.trim="studyWeakness" type="text" placeholder="例如：主旨题、连读、语调不稳" />
        </label>
        <label>
          <span>{{ selectedTask.unitLabel }}</span>
          <input v-model.number="targetCount" type="number" min="1" max="50" />
        </label>
        <label>
          <span>专注时长</span>
          <input v-model.number="focusMinutes" type="range" min="10" max="60" step="5" />
          <b>{{ focusMinutes }} 分钟</b>
        </label>
      </section>

      <section class="companion-preview">
        <div class="buddy-avatar">
          <PetAvatar :pet-id="selectedScene.petId" size="small" />
        </div>
        <div>
          <strong>{{ selectedScene.role }}</strong>
          <p>{{ roleMessage }}</p>
        </div>
      </section>

      <button class="start-btn" :disabled="loadingWords" @click="startSession">
        {{ loadingWords ? '准备任务中...' : '开始专注' }}
      </button>
    </main>

    <main v-else-if="sessionStarted" class="focus-stage">
      <section class="focus-summary">
        <p class="eyebrow">{{ phase === 'focus' ? 'FOCUSING' : 'BREAK TIME' }}</p>
        <h1>{{ taskTitle }}</h1>
        <div class="summary-grid">
          <div><span>当前模式</span><strong>{{ focusMinutes }} 分钟{{ selectedTask.title }}</strong></div>
          <div><span>已完成</span><strong>{{ completedCount }} / {{ targetCount }} 个</strong></div>
          <div><span>正确率</span><strong>{{ accuracy }}%</strong></div>
          <div><span>状态</span><strong>{{ running ? '专注中' : phase === 'break' ? '休息中' : '已暂停' }}</strong></div>
          <div><span>今日专注次数</span><strong>{{ todayFocusCount }}</strong></div>
        </div>
      </section>

      <div class="timer-orbit" :style="{ '--progress': timeProgressText }">
        <div class="timer-core">
          <span>剩余时间</span>
          <strong>{{ formatTime(timeLeft) }}</strong>
          <small>{{ phase === 'focus' ? selectedTask.title : '休息后继续下一轮' }}</small>
        </div>
      </div>

      <section v-if="currentWord && selectedTask.usesWords && phase === 'focus'" class="word-task-panel">
        <div class="task-topline">
          <span>{{ selectedGroup.name }}</span>
          <b>{{ currentIndex + 1 }} / {{ taskWords.length }}</b>
        </div>
        <h2>{{ questionPrompt }}</h2>
        <p v-if="currentWord.phonetic" class="phonetic">{{ currentWord.phonetic }}</p>
        <p v-if="selectedTaskId === 'new'" class="meaning">{{ currentWord.meaning }}</p>
        <p v-if="currentWord.example" class="example">{{ currentWord.example }}</p>

        <div v-if="requiresInput" class="answer-line">
          <input v-model.trim="answerText" :placeholder="answerPlaceholder" @keyup.enter="submitWordAnswer" />
          <button @click="submitWordAnswer">提交</button>
        </div>
        <div v-else class="answer-line compact">
          <button @click="markWordResult(true)">认识 / 掌握</button>
          <button @click="markWordResult(false)">不熟 / 加入错词</button>
        </div>
        <div v-if="wordFeedback" :class="['word-feedback', wordFeedback.type]">{{ wordFeedback.text }}</div>
      </section>

      <section v-else-if="currentStudyStep && phase === 'focus'" class="study-task-panel">
        <div class="task-topline">
          <span>{{ selectedTask.title }}</span>
          <b>{{ currentIndex + 1 }} / {{ taskWords.length }}</b>
        </div>
        <div v-if="matchedMaterial" class="matched-material">
          <strong>{{ matchedTaskTitle }}</strong>
          <p v-if="matchedMaterial.passage">{{ matchedMaterial.passage }}</p>
          <p v-else-if="matchedMaterial.script">{{ matchedMaterial.script }}</p>
          <p v-else-if="matchedMaterial.text">{{ matchedMaterial.text }}</p>
        </div>
        <div v-if="matchedQuestions.length" class="question-list">
          <article v-for="(question, index) in matchedQuestions" :key="index" class="matched-question">
            <strong>{{ index + 1 }}. {{ question.stem || question.question }}</strong>
            <div v-if="question.options?.length" class="question-options">
              <span v-for="option in question.options" :key="option">{{ option }}</span>
            </div>
            <p v-if="question.answer">参考答案：{{ question.answer }}</p>
            <small v-if="question.explanation">{{ question.explanation }}</small>
          </article>
        </div>
        <h2>{{ currentStudyStep.title }}</h2>
        <p>{{ currentStudyStep.detail }}</p>
        <div class="study-tips">
          <span v-for="tip in currentStudyStep.tips" :key="tip">{{ tip }}</span>
        </div>
        <div class="answer-line compact">
          <button @click="markStudyStep(true)">已完成</button>
          <button @click="markStudyStep(false)">需要下次继续</button>
        </div>
        <div v-if="wordFeedback" :class="['word-feedback', wordFeedback.type]">{{ wordFeedback.text }}</div>
      </section>

      <section class="progress-panel">
        <div class="progress-header">
          <span>当前进度</span>
          <b>{{ taskProgress }}%</b>
        </div>
        <div class="task-progress-bar">
          <i :style="{ width: taskProgress + '%' }"></i>
        </div>
        <div class="step-controls">
          <button @click="finishSession">结束并生成报告</button>
          <button @click="completeTask">完成本轮任务</button>
        </div>
      </section>

      <div class="primary-controls">
        <button @click="toggleRunning">{{ running ? '暂停' : '继续' }}</button>
        <button @click="resetPhase">重置时间</button>
        <button @click="nextPhase">切换阶段</button>
        <button @click="backToSetup">换任务</button>
      </div>

      <section class="noise-panel">
        <div class="noise-header">
          <span>{{ selectedScene.noiseLabel }}</span>
          <button :class="{ active: noiseOn }" @click="toggleNoise">{{ noiseOn ? '关闭' : '开启' }}</button>
        </div>
        <div class="noise-options">
          <button
            v-for="item in noises"
            :key="item.id"
            :class="{ active: noiseType === item.id }"
            @click="setNoise(item.id)"
          >
            {{ item.label }}
          </button>
        </div>
        <label class="volume-row">
          <span>音量</span>
          <input v-model.number="volume" type="range" min="0" max="0.35" step="0.01" @input="updateVolume" />
        </label>
      </section>

      <div v-if="rewardNotice" class="reward-toast">{{ rewardNotice }}</div>
    </main>

    <main v-else class="report-stage">
      <p class="eyebrow">STUDY REPORT</p>
      <h1>这轮番茄报告</h1>
      <section class="report-card">
        <div><span>学习时长</span><strong>{{ formatTime(report.duration_seconds) }}</strong></div>
        <div><span>完成数量</span><strong>{{ report.completed_count }} / {{ report.target_count }}</strong></div>
        <div><span>正确率</span><strong>{{ Math.round(report.accuracy * 100) }}%</strong></div>
        <div><span>新增错词</span><strong>{{ report.wrong_count }}</strong></div>
        <div><span>咖啡豆</span><strong>+{{ report.coffee_beans }}</strong></div>
        <div><span>能量值</span><strong>+{{ report.energy_value }}</strong></div>
      </section>
      <section class="recommend-card">
        <strong>下一轮推荐</strong>
        <p>{{ report.recommendation }}</p>
      </section>
      <div class="primary-controls">
        <button @click="startRecommendedTask">按推荐继续</button>
        <button @click="clearReport">重新选择任务</button>
        <button @click="goHome">回到首页</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import DraggablePet from '../components/DraggablePet.vue'
import PetAvatar from '../components/PetAvatar.vue'
import { pomodoroAPI } from '../utils/api'
import { addFocusSession, addInterruption, addRewards, loadGameState, resolveCompanionState } from '../utils/gamification'

const router = useRouter()
const taskTemplates = [
  { id: 'new', icon: '📘', title: '新词学习', description: '看释义和例句，标记掌握', count: 20, usesWords: true, unitLabel: '目标数量' },
  { id: 'wrong', icon: '📖', title: '错词复习', description: '优先复习错题本', count: 15, usesWords: true, unitLabel: '目标数量' },
  { id: 'test', icon: '📝', title: '单词测评', description: '看中文选/填英文', count: 10, usesWords: true, unitLabel: '目标题数' },
  { id: 'spell', icon: '✍️', title: '拼写训练', description: '根据中文拼写英文', count: 10, usesWords: true, unitLabel: '目标数量' },
  { id: 'reading', icon: '📚', title: '阅读理解', description: '限时读文章，完成主旨和细节题', count: 4, usesWords: false, unitLabel: '阅读步骤' },
  { id: 'cloze7', icon: '🧩', title: '七选五训练', description: '梳理段落逻辑和上下文衔接', count: 5, usesWords: false, unitLabel: '训练步骤' },
  { id: 'listening', icon: '🎧', title: '英语精听', description: '听写、核对、复盘关键词', count: 5, usesWords: false, unitLabel: '精听步骤' },
  { id: 'shadowing', icon: '🎙️', title: '影子跟读', description: '逐句模仿语音语调和连读', count: 6, usesWords: false, unitLabel: '跟读步骤' }
]
const studyTaskLibrary = {
  reading: [
    { title: '快速扫读文章', detail: '先用 3 分钟浏览标题、首尾段和每段首句，判断文章主题。', tips: ['标记主题词', '不要逐词翻译'] },
    { title: '完成主旨题', detail: '写下文章主旨或选择最贴近中心的选项。', tips: ['排除局部细节', '关注作者态度'] },
    { title: '定位细节题', detail: '回到原文定位数字、转折、因果和专有名词。', tips: ['圈出定位句', '检查同义替换'] },
    { title: '整理生词和长难句', detail: '记录 3 个影响理解的词或 1 句长难句，留给下一轮复习。', tips: ['只记关键障碍', '用自己的话复述'] }
  ],
  cloze7: [
    { title: '通读全文结构', detail: '先判断文章是问题解决、总分、时间线还是观点论证。', tips: ['看首尾段', '找连接词'] },
    { title: '标出空前空后线索', detail: '关注代词指代、转折、并列、递进和复现词。', tips: ['this/they/it', 'however/also'] },
    { title: '先做确定项', detail: '把最确定的选项先放进去，减少干扰。', tips: ['不要平均用力', '先拿稳分'] },
    { title: '检查段落连贯', detail: '把答案带回原文读一遍，检查语气和逻辑是否顺。', tips: ['上下句必须接得上'] },
    { title: '复盘错因', detail: '记录一个错因：指代没看清、逻辑词忽略、主题偏离或词汇障碍。', tips: ['错因比答案重要'] }
  ],
  listening: [
    { title: '第一遍泛听', detail: '不暂停，抓主题、场景、人物关系和态度。', tips: ['只听大意', '别急着查词'] },
    { title: '第二遍逐句听写', detail: '每 5 到 8 秒暂停一次，写下听到的关键词或整句。', tips: ['先写实词', '空缺留白'] },
    { title: '对照原文修正', detail: '核对漏听、弱读、连读和不熟悉表达。', tips: ['标出漏听点', '关注连读'] },
    { title: '跟读重点句', detail: '选 3 句进行模仿，尽量贴近节奏和重音。', tips: ['先慢后快', '重音明显'] },
    { title: '整理听力词块', detail: '记录 3 个高频词块或场景表达。', tips: ['短语优先', '下次复听'] }
  ],
  shadowing: [
    { title: '选择跟读片段', detail: '选择 30 到 60 秒音频或台词，先听一遍确认语速。', tips: ['短材料更好', '难度适中'] },
    { title: '标记重音和停顿', detail: '在文本上标出重读词、停顿和升降调。', tips: ['重读实词', '停顿分组'] },
    { title: '逐句慢速模仿', detail: '一句一句跟读，先追准确度，不急着追速度。', tips: ['嘴型打开', '跟上节奏'] },
    { title: '同步影子跟读', detail: '尽量与原音频同时开口，落后半拍也可以。', tips: ['不中断', '保持语流'] },
    { title: '录音自检', detail: '录一遍自己的声音，检查重音、连读和尾音。', tips: ['听差距', '只改一处'] },
    { title: '完成复读', detail: '最后完整跟读一遍，记录今天最明显的进步点。', tips: ['完整收尾', '给自己反馈'] }
  ]
}
const scenes = [
  { id: 'library', name: '安静图书馆', role: '书页同学', petId: 'pet_cloud', noiseType: 'pink', noiseLabel: '轻柔翻书声', mood: '安静、稳定' },
  { id: 'cafe', name: '雨夜咖啡馆', role: '小咖啡人', petId: 'pet_coffee', noiseType: 'rain', noiseLabel: '雨声和咖啡馆底噪', mood: '温暖、陪伴' },
  { id: 'morning', name: '晨间自习室', role: '晨光学伴', petId: 'pet_cloud', noiseType: 'forest', noiseLabel: '清晨环境声', mood: '清爽、轻快' },
  { id: 'desk', name: '深夜书桌', role: '台灯学长', petId: 'pet_lamp', noiseType: 'brown', noiseLabel: '低频夜读声', mood: '沉静、收束' },
  { id: 'white', name: '白噪音空间', role: '白噪音助手', petId: 'pet_cloud', noiseType: 'pink', noiseLabel: '纯白噪音', mood: '干净、隔离' }
]
const fallbackGroups = [
  { id: 'level_1', name: '小学高频词汇', desc: '基础新词和日常词汇' },
  { id: 'level_2', name: '初中高频词汇', desc: '核心常用词汇' },
  { id: 'level_3', name: '高中高频词汇', desc: '进阶阅读词汇' },
  { id: 'wrong', name: '我的错词本', desc: '登录后读取错词' }
]
const noises = [
  { id: 'rain', label: '雨声' },
  { id: 'forest', label: '森林' },
  { id: 'brown', label: '低频' },
  { id: 'pink', label: '柔和' }
]

const selectedSceneId = ref('cafe')
const selectedTaskId = ref('wrong')
const selectedGroupId = ref('wrong')
const wordGroups = ref(fallbackGroups)
const taskTitle = ref('复习四级核心词 Unit 3')
const targetCount = ref(15)
const completedCount = ref(0)
const correctCount = ref(0)
const sessionStarted = ref(false)
const focusMinutes = ref(25)
const breakMinutes = ref(5)
const phase = ref('focus')
const timeLeft = ref(focusMinutes.value * 60)
const running = ref(false)
const todayFocusCount = ref(0)
const coffeeBeans = ref(0)
const energyValue = ref(0)
const gameState = ref(loadGameState())
const rewardNotice = ref('')
const interrupted = ref(false)
const noiseOn = ref(false)
const noiseType = ref('rain')
const volume = ref(0.12)
const loadingWords = ref(false)
const taskWords = ref([])
const matchedTask = ref(null)
const studyLevel = ref('高中')
const studyTopic = ref('校园生活')
const studyWeakness = ref('')
const currentIndex = ref(0)
const answerText = ref('')
const wordFeedback = ref(null)
const results = ref([])
const sessionStartTime = ref(null)
const report = ref(null)
let timer = null
let audioContext = null
let noiseSource = null
let gainNode = null
let filterNode = null

const selectedTask = computed(() => taskTemplates.find((task) => task.id === selectedTaskId.value) || taskTemplates[0])
const selectedScene = computed(() => scenes.find((scene) => scene.id === selectedSceneId.value) || scenes[0])
const selectedGroup = computed(() => wordGroups.value.find((group) => group.id === selectedGroupId.value) || wordGroups.value[0])
const currentWord = computed(() => taskWords.value[currentIndex.value])
const currentStudyStep = computed(() => selectedTask.value.usesWords ? null : taskWords.value[currentIndex.value])
const matchedMaterial = computed(() => matchedTask.value?.material || null)
const matchedQuestions = computed(() => matchedTask.value?.questions || [])
const matchedTaskTitle = computed(() => matchedTask.value?.title || taskTitle.value)
const totalSeconds = computed(() => (phase.value === 'focus' ? focusMinutes.value : breakMinutes.value) * 60)
const timeProgressText = computed(() => `${Math.round(((totalSeconds.value - timeLeft.value) / totalSeconds.value) * 100)}%`)
const taskProgress = computed(() => Math.min(100, Math.round((completedCount.value / Math.max(targetCount.value, 1)) * 100)))
const accuracy = computed(() => (completedCount.value ? Math.round((correctCount.value / completedCount.value) * 100) : 0))
const requiresInput = computed(() => ['test', 'spell'].includes(selectedTaskId.value))
const answerPlaceholder = computed(() => selectedTaskId.value === 'spell' ? '请输入英文拼写' : '请输入英文单词')
const currentWrongCount = computed(() => {
  if (report.value) return report.value.wrong_count || 0
  return results.value.filter((item) => !item.is_correct).length
})
const questionPrompt = computed(() => {
  if (!currentWord.value) return '本轮任务已完成'
  if (selectedTaskId.value === 'new') return currentWord.value.word
  return currentWord.value.meaning
})
const companionState = computed(() => {
  if (interrupted.value && (gameState.value.todayInterruptions || 0) < 2) {
    return {
      id: 'warning',
      mood: 'warning',
      label: '轻量建议',
      message: '这次中断了，要不要改成 10 分钟轻量任务？'
    }
  }
  return resolveCompanionState({
    phase: sessionStarted.value ? phase.value : 'idle',
    running: running.value,
    completed: completedCount.value >= targetCount.value && sessionStarted.value,
    report: report.value,
    wrongCount: currentWrongCount.value,
    gameState: gameState.value
  })
})
const roleMessage = computed(() => companionState.value.message)

onMounted(async () => {
  syncGameState(loadGameState())
  const storedTask = localStorage.getItem('pomodoro_task')
  if (storedTask && taskTemplates.some((task) => task.id === storedTask)) {
    selectTask(storedTask)
    localStorage.removeItem('pomodoro_task')
  }
  try {
    const response = await pomodoroAPI.groups()
    if (response.data.success) wordGroups.value = response.data.groups
  } catch (error) {
    console.error('获取词组失败', error)
  }
})

onUnmounted(() => {
  stopTimer()
  stopNoise()
})

const selectTask = (taskId) => {
  const task = taskTemplates.find((item) => item.id === taskId)
  selectedTaskId.value = taskId
  taskTitle.value = task.usesWords ? `${selectedGroup.value.name} · ${task.title}` : `${task.title} · 25 分钟训练`
  targetCount.value = task.count
  completedCount.value = 0
}

const selectGroup = (groupId) => {
  selectedGroupId.value = groupId
  if (selectedTask.value.usesWords) taskTitle.value = `${selectedGroup.value.name} · ${selectedTask.value.title}`
}

const selectScene = (sceneId) => {
  selectedSceneId.value = sceneId
  noiseType.value = selectedScene.value.noiseType
}

const startSession = async () => {
  if (selectedTask.value.usesWords) {
    loadingWords.value = true
    try {
      const response = await pomodoroAPI.start({
        group: selectedGroupId.value,
        task_type: selectedTaskId.value,
        limit: targetCount.value
      })
      if (response.data.success) {
        taskWords.value = response.data.words || []
      }
    } catch (error) {
      console.error('加载单词失败', error)
      taskWords.value = []
    } finally {
      loadingWords.value = false
    }
  } else {
    loadingWords.value = true
    try {
      const response = await pomodoroAPI.matchTask({
        task_type: selectedTaskId.value,
        level: studyLevel.value,
        topic: studyTopic.value || selectedTask.value.title,
        weakness: studyWeakness.value,
        count: targetCount.value
      })
      if (response.data.success && response.data.task) {
        matchedTask.value = response.data.task
        taskWords.value = (response.data.task.steps || []).slice(0, targetCount.value)
        if (response.data.task.title) taskTitle.value = response.data.task.title
      }
    } catch (error) {
      console.error('AI 匹配任务失败，使用本地任务清单', error)
    } finally {
      loadingWords.value = false
    }
    if (!taskWords.value.length) {
      matchedTask.value = null
      const steps = studyTaskLibrary[selectedTaskId.value] || []
      taskWords.value = steps.slice(0, targetCount.value)
    }
  }
  if (!taskWords.value.length) {
    alert(selectedTask.value.usesWords ? '当前词组没有可用单词，请换一个词组或检查后端词库。' : '当前任务暂时没有可用步骤，请换一个任务。')
    return
  }
  if (!taskTitle.value) taskTitle.value = selectedTask.value.usesWords ? `${selectedGroup.value.name} · ${selectedTask.value.title}` : `${selectedTask.value.title} · 25 分钟训练`
  targetCount.value = Math.min(targetCount.value || selectedTask.value.count, taskWords.value.length)
  phase.value = 'focus'
  timeLeft.value = focusMinutes.value * 60
  completedCount.value = 0
  correctCount.value = 0
  currentIndex.value = 0
  answerText.value = ''
  wordFeedback.value = null
  results.value = []
  if (selectedTask.value.usesWords) matchedTask.value = null
  report.value = null
  interrupted.value = false
  rewardNotice.value = ''
  sessionStartTime.value = Date.now()
  sessionStarted.value = true
  toggleRunning()
}

const markWordResult = (isCorrect) => {
  if (!currentWord.value || wordFeedback.value) return
  results.value.push({
    word_id: currentWord.value.id,
    word: currentWord.value.word,
    meaning: currentWord.value.meaning,
    is_correct: isCorrect,
    user_answer: isCorrect ? 'known' : 'unknown'
  })
  completedCount.value += 1
  if (isCorrect) correctCount.value += 1
  wordFeedback.value = {
    type: isCorrect ? 'correct' : 'wrong',
    text: isCorrect ? '已记录掌握。' : `已加入错词：${currentWord.value.word} - ${currentWord.value.meaning}`
  }
  setTimeout(nextWord, 650)
}

const submitWordAnswer = () => {
  if (!answerText.value || !currentWord.value || wordFeedback.value) return
  const normalized = answerText.value.trim().toLowerCase()
  const correct = normalized === currentWord.value.word.toLowerCase()
  results.value.push({
    word_id: currentWord.value.id,
    word: currentWord.value.word,
    meaning: currentWord.value.meaning,
    is_correct: correct,
    user_answer: answerText.value
  })
  completedCount.value += 1
  if (correct) correctCount.value += 1
  wordFeedback.value = {
    type: correct ? 'correct' : 'wrong',
    text: correct ? '回答正确。' : `正确答案：${currentWord.value.word}`
  }
  setTimeout(nextWord, 900)
}

const nextWord = () => {
  if (completedCount.value >= targetCount.value || currentIndex.value >= taskWords.value.length - 1) {
    finishSession()
    return
  }
  currentIndex.value += 1
  answerText.value = ''
  wordFeedback.value = null
}

const markStudyStep = (finished) => {
  if (!currentStudyStep.value || wordFeedback.value) return
  results.value.push({
    step_id: currentIndex.value + 1,
    title: currentStudyStep.value.title,
    task_type: selectedTaskId.value,
    is_correct: finished,
    user_answer: finished ? 'completed' : 'needs_followup'
  })
  completedCount.value += 1
  if (finished) correctCount.value += 1
  wordFeedback.value = {
    type: finished ? 'correct' : 'wrong',
    text: finished ? '这一步已完成，继续保持节奏。' : '已记录为下次继续，先把这一轮稳定收尾。'
  }
  setTimeout(nextWord, 700)
}

const completeTask = () => {
  while (completedCount.value < targetCount.value && taskWords.value[currentIndex.value]) {
    if (selectedTask.value.usesWords) {
      results.value.push({
        word_id: currentWord.value.id,
        word: currentWord.value.word,
        meaning: currentWord.value.meaning,
        is_correct: true,
        user_answer: 'completed'
      })
    } else {
      results.value.push({
        step_id: currentIndex.value + 1,
        title: currentStudyStep.value.title,
        task_type: selectedTaskId.value,
        is_correct: true,
        user_answer: 'completed'
      })
    }
    completedCount.value += 1
    correctCount.value += 1
    if (currentIndex.value < taskWords.value.length - 1) currentIndex.value += 1
    else break
  }
  finishSession()
}

const finishSession = async () => {
  stopTimer()
  const duration = sessionStartTime.value ? Math.round((Date.now() - sessionStartTime.value) / 1000) : 0
  let payloadReport = {
    duration_seconds: duration,
    target_count: targetCount.value,
    completed_count: completedCount.value,
    correct_count: correctCount.value,
    accuracy: completedCount.value ? correctCount.value / completedCount.value : 0,
    wrong_count: results.value.filter((item) => !item.is_correct).length,
    coffee_beans: Math.max(3, Math.floor(completedCount.value / 2)),
    energy_value: Math.max(5, completedCount.value),
    recommendation: buildLocalRecommendation()
  }
  try {
    const response = await pomodoroAPI.submit({
      group: selectedGroupId.value,
      task_type: selectedTaskId.value,
      target_count: targetCount.value,
      duration_seconds: duration,
      results: results.value,
      matched_title: matchedTask.value?.title || '',
      matched_source: matchedTask.value?.source || ''
    })
    if (response.data.success) {
      payloadReport = {
        ...response.data.record,
        wrong_count: response.data.wrong_count,
        coffee_beans: response.data.coffee_beans,
        energy_value: response.data.energy_value,
        recommendation: response.data.recommendation
      }
    }
  } catch (error) {
    console.error('提交番茄报告失败，使用本地报告', error)
  }
  syncGameState(addFocusSession())
  grantReward(payloadReport.coffee_beans, payloadReport.energy_value)
  report.value = payloadReport
  sessionStarted.value = false
  phase.value = 'focus'
}

const buildLocalRecommendation = () => {
  const wrongCount = results.value.filter((item) => !item.is_correct).length
  if (!selectedTask.value.usesWords) return buildStudyRecommendation(selectedTaskId.value, wrongCount)
  if (wrongCount) return `下一轮建议复习 ${wrongCount} 个错词，优先做错词复习。`
  if (accuracy.value >= 90) return '这一轮掌握很好，下一轮可以切换到新词学习。'
  return '建议下一轮做 10 题单词测评，检查刚刚的记忆效果。'
}

const buildStudyRecommendation = (taskType, unfinishedCount) => {
  if (unfinishedCount) return `这轮还有 ${unfinishedCount} 个步骤需要继续，下一轮建议开 10 分钟轻量任务补完。`
  const map = {
    reading: '阅读状态不错，下一轮可以做七选五，继续训练段落逻辑。',
    cloze7: '七选五完成得很稳，下一轮建议做阅读理解，把逻辑线索迁移到长文章。',
    listening: '精听完成后建议立刻做 5 分钟影子跟读，巩固语音和词块。',
    shadowing: '跟读完成得不错，下一轮可以切到英语精听，检查自己是否真正听清。'
  }
  return map[taskType] || '这轮学习完成了，下一轮可以切换到单词测评检查基础。'
}

const startRecommendedTask = () => {
  if (selectedTask.value.usesWords) {
    selectedTaskId.value = results.value.some((item) => !item.is_correct) ? 'wrong' : 'test'
    selectedGroupId.value = results.value.some((item) => !item.is_correct) ? 'wrong' : selectedGroupId.value
  } else {
    const nextMap = {
      reading: 'cloze7',
      cloze7: 'reading',
      listening: 'shadowing',
      shadowing: 'listening'
    }
    selectedTaskId.value = nextMap[selectedTaskId.value] || 'test'
  }
  const nextTask = taskTemplates.find((item) => item.id === selectedTaskId.value) || selectedTask.value
  taskTitle.value = nextTask.usesWords ? `${selectedGroup.value.name} · ${nextTask.title}` : `${nextTask.title} · 25 分钟训练`
  targetCount.value = nextTask.count
  clearReport()
}

const clearReport = () => {
  report.value = null
  sessionStarted.value = false
  phase.value = 'focus'
  timeLeft.value = focusMinutes.value * 60
}

const backToSetup = () => {
  stopTimer()
  if (completedCount.value < targetCount.value && phase.value === 'focus') {
    interrupted.value = true
    focusMinutes.value = Math.min(focusMinutes.value, 10)
  }
  sessionStarted.value = false
  phase.value = 'focus'
  timeLeft.value = focusMinutes.value * 60
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

const toggleRunning = () => {
  if (running.value) {
    stopTimer()
    return
  }
  running.value = true
  timer = setInterval(() => {
    if (timeLeft.value <= 1) {
      finishSession()
      return
    }
    timeLeft.value -= 1
  }, 1000)
}

const stopTimer = () => {
  if (timer) clearInterval(timer)
  timer = null
  running.value = false
}

const resetPhase = () => {
  stopTimer()
  timeLeft.value = totalSeconds.value
}

const nextPhase = () => {
  if (phase.value === 'focus') {
    finishSession()
  } else {
    phase.value = 'focus'
    timeLeft.value = totalSeconds.value
  }
}

const grantReward = (beans, energy) => {
  rewardNotice.value = `获得 ${beans} 颗咖啡豆，能量 +${energy}`
  syncGameState(addRewards({ beans, energy }))
  setTimeout(() => {
    rewardNotice.value = ''
  }, 2600)
}

const syncGameState = (state) => {
  gameState.value = state
  todayFocusCount.value = state.todayFocusCount
  coffeeBeans.value = state.coffeeBeans
  energyValue.value = state.energyValue
}

const handleExit = () => {
  if (sessionStarted.value && completedCount.value < targetCount.value && phase.value === 'focus' && !interrupted.value) {
    syncGameState(addInterruption())
    interrupted.value = true
    focusMinutes.value = Math.min(focusMinutes.value, 10)
    stopTimer()
    return
  }
  goHome()
}

const goHome = () => {
  stopTimer()
  stopNoise()
  router.push('/')
}

const toggleNoise = async () => {
  if (noiseOn.value) {
    stopNoise()
    return
  }
  await startNoise()
}

const setNoise = async (type) => {
  noiseType.value = type
  if (noiseOn.value) {
    stopNoise()
    await startNoise()
  }
}

const startNoise = async () => {
  audioContext = new AudioContext()
  gainNode = audioContext.createGain()
  filterNode = audioContext.createBiquadFilter()
  noiseSource = audioContext.createBufferSource()
  noiseSource.buffer = createNoiseBuffer(audioContext, noiseType.value)
  noiseSource.loop = true
  configureFilter(noiseType.value)
  gainNode.gain.value = volume.value
  noiseSource.connect(filterNode)
  filterNode.connect(gainNode)
  gainNode.connect(audioContext.destination)
  noiseSource.start()
  noiseOn.value = true
}

const stopNoise = () => {
  if (noiseSource) noiseSource.stop()
  if (audioContext) audioContext.close()
  noiseSource = null
  audioContext = null
  gainNode = null
  filterNode = null
  noiseOn.value = false
}

const updateVolume = () => {
  if (gainNode) gainNode.gain.value = volume.value
}

const configureFilter = (type) => {
  const config = {
    rain: ['bandpass', 950, 0.8],
    forest: ['bandpass', 520, 1.4],
    brown: ['lowpass', 420, 0.7],
    pink: ['lowpass', 1200, 0.9]
  }[type]
  filterNode.type = config[0]
  filterNode.frequency.value = config[1]
  filterNode.Q.value = config[2]
}

const createNoiseBuffer = (ctx, type) => {
  const seconds = 2
  const buffer = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate)
  const data = buffer.getChannelData(0)
  let last = 0
  for (let i = 0; i < data.length; i += 1) {
    const white = Math.random() * 2 - 1
    if (type === 'brown') {
      last = (last + 0.02 * white) / 1.02
      data[i] = last * 3.5
    } else if (type === 'pink') {
      last = 0.96 * last + 0.04 * white
      data[i] = last
    } else {
      data[i] = white
    }
  }
  return buffer
}
</script>

<style scoped>
.pomodoro-page {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 50% 18%, rgba(255, 255, 255, 0.22), transparent 28%),
    linear-gradient(135deg, #192234 0%, #6b3454 100%);
  color: white;
}

.pomodoro-page.library {
  background: linear-gradient(rgba(17, 24, 39, 0.42), rgba(17, 24, 39, 0.6)), linear-gradient(135deg, #293241 0%, #6b4f3f 100%);
}

.pomodoro-page.cafe {
  background: linear-gradient(rgba(30, 20, 27, 0.28), rgba(30, 20, 27, 0.72)), repeating-linear-gradient(115deg, rgba(255,255,255,.16) 0 1px, transparent 1px 18px), linear-gradient(135deg, #20283e 0%, #7a3c45 100%);
}

.pomodoro-page.morning {
  background: radial-gradient(circle at 18% 18%, rgba(255, 239, 174, 0.46), transparent 24%), linear-gradient(135deg, #4a90a4 0%, #a6d8a8 100%);
}

.pomodoro-page.desk {
  background: radial-gradient(circle at 56% 18%, rgba(255, 211, 129, 0.36), transparent 20%), linear-gradient(135deg, #111827 0%, #4c2436 100%);
}

.pomodoro-page.white {
  background: radial-gradient(circle at 50% 20%, rgba(255, 255, 255, 0.55), transparent 26%), linear-gradient(135deg, #6b7b8c 0%, #dde5ed 100%);
}

.exit-btn {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 90;
  padding: 10px 18px;
  border: 1px solid rgba(255,255,255,.32);
  border-radius: 24px;
  background: rgba(255,255,255,.14);
  color: white;
  backdrop-filter: blur(12px);
}

.task-setup,
.focus-stage,
.report-stage {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 22px;
  min-height: 100vh;
  padding: 56px 20px;
  text-align: center;
}

.eyebrow {
  margin: 0;
  color: rgba(255,255,255,.68);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: .12em;
}

h1 {
  max-width: 920px;
  margin: 0;
  font-size: clamp(34px, 6vw, 68px);
}

.setup-desc {
  max-width: 680px;
  margin: 0;
  color: rgba(255,255,255,.74);
  font-size: 17px;
}

.scene-grid,
.task-grid,
.group-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(130px, 1fr));
  gap: 14px;
  width: min(1120px, 94vw);
}

.group-grid {
  grid-template-columns: repeat(4, minmax(150px, 1fr));
}

.scene-card,
.task-card,
.group-card {
  display: grid;
  align-content: start;
  gap: 10px;
  min-height: 128px;
  padding: 18px;
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 22px;
  background: rgba(255,255,255,.12);
  color: white;
  text-align: left;
  backdrop-filter: blur(14px);
}

.scene-card.active,
.task-card.active,
.group-card.active {
  background: white;
  color: #263247;
  box-shadow: 0 18px 48px rgba(0,0,0,.22);
}

.task-card span {
  font-size: 30px;
}

.task-card strong,
.group-card strong,
.scene-card span {
  font-size: 18px;
}

.task-card small,
.group-card small,
.scene-card small {
  opacity: .74;
  line-height: 1.5;
}

.setup-panel,
.progress-panel,
.noise-panel,
.word-task-panel,
.study-task-panel,
.report-card,
.recommend-card {
  width: min(94vw, 760px);
  padding: 18px;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 20px;
  background: rgba(255,255,255,.12);
  backdrop-filter: blur(14px);
}

.setup-panel {
  display: grid;
  gap: 14px;
}

.setup-panel label,
.volume-row {
  display: grid;
  grid-template-columns: 84px 1fr 76px;
  gap: 12px;
  align-items: center;
  color: rgba(255,255,255,.82);
  text-align: left;
}

.setup-panel input[type="text"],
.setup-panel input[type="number"],
.setup-panel select,
.answer-line input {
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid rgba(255,255,255,.26);
  border-radius: 14px;
  background: rgba(255,255,255,.15);
  color: white;
  outline: none;
}

.setup-panel select {
  appearance: none;
}

.start-btn,
.primary-controls button,
.step-controls button,
.noise-header button,
.noise-options button,
.answer-line button {
  min-height: 44px;
  padding: 0 22px;
  border: 1px solid rgba(255,255,255,.28);
  border-radius: 24px;
  background: rgba(255,255,255,.16);
  color: white;
  font-weight: 700;
  backdrop-filter: blur(10px);
}

.start-btn,
.primary-controls button:first-child,
.step-controls button:first-child,
.noise-header button.active,
.noise-options button.active,
.answer-line button:first-of-type {
  background: white;
  color: #263247;
}

.start-btn:disabled {
  opacity: .62;
}

.companion-preview {
  display: flex;
  align-items: center;
  gap: 14px;
  width: min(94vw, 720px);
  padding: 16px;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 22px;
  background: rgba(255,255,255,.12);
  text-align: left;
  backdrop-filter: blur(14px);
}

.buddy-avatar {
  display: grid;
  flex: 0 0 82px;
  place-items: center;
  width: 82px;
  height: 82px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 12px 30px rgba(0,0,0,.2);
}

.companion-preview p {
  margin: 6px 0 0;
  color: rgba(255,255,255,.75);
  line-height: 1.6;
}

.focus-summary {
  display: grid;
  justify-items: center;
  gap: 18px;
  width: min(94vw, 960px);
}

.summary-grid,
.report-card {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
}

.summary-grid div,
.report-card div {
  padding: 16px;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 18px;
  background: rgba(255,255,255,.12);
}

.summary-grid span,
.report-card span {
  display: block;
  margin-bottom: 8px;
  color: rgba(255,255,255,.62);
  font-size: 13px;
}

.summary-grid strong,
.report-card strong {
  font-size: 18px;
}

.timer-orbit {
  display: grid;
  place-items: center;
  width: min(62vw, 300px);
  aspect-ratio: 1;
  border-radius: 50%;
  background: conic-gradient(#fff var(--progress), rgba(255,255,255,.18) 0);
  box-shadow: 0 24px 90px rgba(0,0,0,.28);
}

.timer-core {
  display: grid;
  place-items: center;
  width: 78%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: rgba(16,22,31,.72);
  backdrop-filter: blur(18px);
}

.timer-core span,
.timer-core small {
  color: rgba(255,255,255,.7);
}

.timer-core strong {
  font-size: clamp(48px, 9vw, 82px);
  line-height: 1;
}

.word-task-panel {
  display: grid;
  gap: 12px;
}

.study-task-panel {
  display: grid;
  gap: 16px;
}

.task-topline,
.progress-header,
.noise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.word-task-panel h2 {
  margin: 6px 0;
  font-size: clamp(30px, 5vw, 52px);
}

.study-task-panel h2 {
  margin: 4px 0 0;
  font-size: clamp(28px, 4vw, 46px);
}

.matched-material {
  display: grid;
  gap: 8px;
  max-width: 720px;
  max-height: 180px;
  overflow: auto;
  padding: 14px;
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 18px;
  background: rgba(13, 18, 29, .26);
  text-align: left;
}

.matched-material strong {
  color: white;
}

.matched-material p {
  margin: 0;
  color: rgba(255,255,255,.76);
  font-size: 14px;
  line-height: 1.7;
}

.question-list {
  display: grid;
  gap: 10px;
  width: min(720px, 100%);
  max-height: 260px;
  overflow: auto;
}

.matched-question {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 16px;
  background: rgba(255,255,255,.1);
  text-align: left;
}

.matched-question strong {
  color: white;
  line-height: 1.5;
}

.matched-question p,
.matched-question small {
  margin: 0;
  color: rgba(255,255,255,.74);
  line-height: 1.6;
}

.question-options {
  display: grid;
  gap: 6px;
}

.question-options span {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255,255,255,.12);
  color: rgba(255,255,255,.82);
  font-size: 13px;
  line-height: 1.45;
}

.study-task-panel p {
  max-width: 620px;
  margin: 0 auto;
  color: rgba(255,255,255,.78);
  font-size: 17px;
  line-height: 1.7;
}

.study-tips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.study-tips span {
  padding: 7px 12px;
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 999px;
  background: rgba(255,255,255,.12);
  color: rgba(255,255,255,.82);
  font-size: 13px;
  font-weight: 800;
}

.phonetic,
.example,
.meaning {
  margin: 0;
  color: rgba(255,255,255,.76);
}

.meaning {
  font-size: 22px;
  font-weight: 800;
}

.answer-line {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.answer-line input {
  width: min(460px, 70vw);
}

.answer-line.compact {
  flex-wrap: wrap;
}

.word-feedback {
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255,255,255,.14);
  font-weight: 800;
}

.word-feedback.correct {
  color: #b9f6ca;
}

.word-feedback.wrong {
  color: #ffccbc;
}

.task-progress-bar {
  height: 12px;
  overflow: hidden;
  border-radius: 99px;
  background: rgba(255,255,255,.18);
}

.task-progress-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: white;
  transition: width .2s ease;
}

.primary-controls,
.step-controls,
.noise-options {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.noise-panel {
  display: grid;
  gap: 14px;
}

.reward-toast {
  position: fixed;
  left: 50%;
  bottom: 26px;
  transform: translateX(-50%);
  padding: 12px 18px;
  border-radius: 24px;
  background: white;
  color: #263247;
  font-weight: 800;
  box-shadow: 0 16px 40px rgba(0,0,0,.22);
}

.report-card {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.recommend-card {
  color: white;
}

.recommend-card p {
  margin: 8px 0 0;
  color: rgba(255,255,255,.78);
}

input[type="range"] {
  accent-color: white;
}

@media (max-width: 980px) {
  .scene-grid,
  .task-grid,
  .group-grid,
  .summary-grid,
  .report-card {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .exit-btn {
    top: 14px;
    right: 14px;
  }

  .scene-grid,
  .task-grid,
  .group-grid,
  .summary-grid,
  .report-card {
    grid-template-columns: 1fr;
  }

  .setup-panel label,
  .volume-row,
  .answer-line {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .answer-line input {
    width: 100%;
  }
}
</style>
