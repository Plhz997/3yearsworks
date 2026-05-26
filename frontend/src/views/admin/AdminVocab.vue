<template>
  <div class="admin-container">
    <div class="sidebar">
      <div class="logo">
        <h2>管理后台</h2>
      </div>
      <nav class="nav">
        <button @click="goTo('/admin')" class="nav-item">📊 仪表盘</button>
        <button @click="goTo('/admin/users')" class="nav-item">👥 用户管理</button>
        <button @click="goTo('/admin/vocab')" class="nav-item active">📖 词库管理</button>
        <button @click="goTo('/admin/records')" class="nav-item">📝 测评记录</button>
        <button @click="goTo('/admin/stats')" class="nav-item">📈 数据统计</button>
      </nav>
      <button @click="logout" class="logout-btn">退出登录</button>
    </div>
    
    <div class="main-content">
      <div class="header">
        <h1>词库管理</h1>
        <div class="header-actions">
          <button @click="openUpload" class="upload-btn">📂 批量上传</button>
          <button @click="showAddModal = true" class="add-btn">+ 添加单词</button>
        </div>
      </div>
      
      <div class="filter-bar">
        <select v-model="filterLevel" @change="loadVocab">
          <option value="">全部学段</option>
          <option value="1">小学</option>
          <option value="2">初中</option>
          <option value="3">高中</option>
        </select>
        <input v-model="searchKeyword" type="text" placeholder="搜索单词" @keyup.enter="loadVocab">
        <button @click="loadVocab" class="search-btn">搜索</button>
      </div>
      
      <div v-if="selectedIds.length > 0" class="batch-bar">
        <span class="batch-info">已选择 {{ selectedIds.length }} 项</span>
        <button @click="selectAllVocab" class="btn-small">全选本页</button>
        <button @click="selectedIds = []" class="btn-small">取消选择</button>
        <button @click="batchDelete" class="btn-danger">批量删除</button>
      </div>
      
      <div class="vocab-table">
        <table>
          <thead>
            <tr>
              <th width="40">
                <input type="checkbox" :checked="isAllSelected" @change="toggleAllSelect">
              </th>
              <th>ID</th>
              <th>单词</th>
              <th>释义</th>
              <th>音标</th>
              <th>学段</th>
              <th>词频</th>
              <th>难度</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="word in vocabList" :key="word.id">
              <td>
                <input type="checkbox" :value="word.id" v-model="selectedIds">
              </td>
              <td>{{ word.id }}</td>
              <td>{{ word.word }}</td>
              <td>{{ word.meaning }}</td>
              <td>{{ word.phonetic || '-' }}</td>
              <td><span class="level-badge" :class="`level-${word.level}`">{{ getLevelName(word.level) }}</span></td>
              <td>{{ word.frequency }}</td>
              <td>{{ word.difficulty }}</td>
              <td>
                <button @click="editWord(word)" class="edit-btn">编辑</button>
                <button @click="deleteWord(word.id)" class="delete-btn">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="showAddModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ editingWord ? '编辑单词' : '添加单词' }}</h3>
            <button @click="closeModal" class="close-btn">×</button>
          </div>
          <form @submit.prevent="saveWord">
            <div class="form-group">
              <label>单词</label>
              <input v-model="form.word" type="text" required>
            </div>
            <div class="form-group">
              <label>释义</label>
              <input v-model="form.meaning" type="text" required>
            </div>
            <div class="form-group">
              <label>音标</label>
              <input v-model="form.phonetic" type="text">
            </div>
            <div class="form-group">
              <label>例句</label>
              <textarea v-model="form.example"></textarea>
            </div>
            <div class="form-group">
              <label>学段</label>
              <select v-model="form.level">
                <option value="1">小学</option>
                <option value="2">初中</option>
                <option value="3">高中</option>
              </select>
            </div>
            <div class="form-group">
              <label>词频等级</label>
              <input v-model.number="form.frequency" type="number" min="1" max="5" value="3">
            </div>
            <div class="form-group">
              <label>难度等级</label>
              <input v-model.number="form.difficulty" type="number" min="1" max="5" value="3">
            </div>
            <button type="submit" class="submit-btn">保存</button>
          </form>
        </div>
      </div>
    <!-- 批量上传弹窗 -->
      <div v-if="showUploadModal" class="modal upload-modal">
        <div class="modal-content upload-content">
          <div class="modal-header">
            <h3>批量上传词库</h3>
            <button @click="closeUpload" class="close-btn">×</button>
          </div>

          <!-- 步骤1: 选择文件 -->
          <div v-if="uploadStep === 1" class="upload-step">
            <div class="level-select-row">
              <label>统一学段：</label>
              <select v-model="uploadLevel" class="level-select">
                <option :value="1">小学</option>
                <option :value="2">初中</option>
                <option :value="3">高中</option>
              </select>
              <span class="level-hint">上传后所有单词将设为该学段，也可在预览中逐条修改</span>
            </div>
            <div class="upload-area" @click="fileInput.click()" @dragover.prevent @drop.prevent="handleDrop">
              <input ref="fileInput" type="file" accept=".txt,.csv,.tsv" @change="handleFileSelect" style="display:none">
              <div class="upload-icon">📁</div>
              <p class="upload-text">点击选择文件或拖拽文件到此处</p>
              <p class="upload-hint">支持 .txt / .csv / .tsv 格式</p>
              <p v-if="selectedFile" class="selected-file">已选择：{{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})</p>
            </div>
            <div class="format-tips">
              <h4>支持的文件格式：</h4>
              <ul>
                <li>CSV格式：<code>word,meaning,phonetic,example</code></li>
                <li>空格分隔：<code>apple 苹果</code></li>
                <li>Tab分隔：<code>apple&nbsp;&nbsp;&nbsp;&nbsp;苹果</code></li>
                <li>中划线：<code>apple - 苹果</code></li>
                <li>冒号分隔：<code>apple: 苹果</code> / <code>apple：苹果</code></li>
                <li>编号列表：<code>1. apple 苹果</code></li>
              </ul>
              <p class="tip-note">系统会自动识别格式并解析，每个文件可包含多条单词</p>
            </div>
            <div class="upload-actions">
              <button @click="closeUpload" class="btn-cancel">取消</button>
              <button @click="doUpload" :disabled="!selectedFile || uploading" class="btn-primary">
                <span v-if="uploading">解析中...</span>
                <span v-else>开始解析</span>
              </button>
            </div>
          </div>

          <!-- 步骤2: 预览结果 -->
          <div v-if="uploadStep === 2" class="preview-step">
            <div class="preview-summary">
              <div class="summary-left">
                <span class="summary-badge success">识别格式：{{ detectedFormat }}</span>
                <span class="summary-badge info">共 {{ parsedTotal }} 条</span>
                <span class="summary-badge new">新增 {{ parsedNew }} 条</span>
                <span v-if="parsedDup > 0" class="summary-badge dup">重复 {{ parsedDup }} 条</span>
              </div>
              <div class="summary-right">
                <button @click="selectAll" class="btn-small">全选</button>
                <button @click="deselectAll" class="btn-small">取消全选</button>
                <button @click="toggleDupOnly" class="btn-small btn-warn">{{ showDupOnly ? '显示全部' : '仅看重复' }}</button>
              </div>
            </div>

            <div class="preview-table-wrapper">
              <table class="preview-table">
                <thead>
                  <tr>
                    <th width="30">选择</th>
                    <th width="120">单词</th>
                    <th width="160">释义</th>
                    <th width="100">音标</th>
                    <th width="80">学段</th>
                    <th width="50">词频</th>
                    <th width="50">难度</th>
                    <th width="60">例句</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(pw, idx) in filteredPreview" :key="idx"
                      :class="{ 'row-dup': pw.duplicate }">
                    <td>
                      <input type="checkbox" v-model="pw._selected" :disabled="pw.duplicate">
                    </td>
                    <td>{{ pw.word }}</td>
                    <td>
                      <input v-model="pw.meaning" class="inline-edit" @input="pw._edited = true">
                    </td>
                    <td>
                      <input v-model="pw.phonetic" class="inline-edit" placeholder="(可选)">
                    </td>
                    <td>
                      <select v-model="pw.level" class="inline-select">
                        <option :value="1">小学</option>
                        <option :value="2">初中</option>
                        <option :value="3">高中</option>
                      </select>
                    </td>
                    <td>
                      <input v-model.number="pw.frequency" type="number" min="1" max="5" class="inline-edit small">
                    </td>
                    <td>
                      <input v-model.number="pw.difficulty" type="number" min="1" max="5" class="inline-edit small">
                    </td>
                    <td>
                      <input v-model="pw.example" class="inline-edit" placeholder="(可选)">
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="preview-actions">
              <button @click="uploadStep = 1" class="btn-cancel">返回上一步</button>
              <div>
                <span class="selected-count">已选择 {{ selectedCount }} 条</span>
                <button @click="doImport" :disabled="selectedCount === 0 || importing" class="btn-primary">
                  <span v-if="importing">导入中...</span>
                  <span v-else>确认导入 ({{ selectedCount }})</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 步骤3: 完成 -->
          <div v-if="uploadStep === 3" class="done-step">
            <div class="done-icon">✅</div>
            <h3>导入完成</h3>
            <p>成功导入 {{ importResult.success }} 条，跳过 {{ importResult.skipped }} 条</p>
            <button @click="closeUploadAndRefresh" class="btn-primary">完成</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { vocabAPI } from '../../utils/api'

const router = useRouter()

const vocabList = ref([])
const filterLevel = ref('')
const searchKeyword = ref('')
const selectedIds = ref([])
const showAddModal = ref(false)
const editingWord = ref(null)
const form = ref({
  word: '',
  meaning: '',
  phonetic: '',
  example: '',
  level: '2',
  frequency: 3,
  difficulty: 3
})

onMounted(() => {
  if (!localStorage.getItem('access_token')) {
    router.push('/admin/login')
    return
  }
  loadVocab()
})

const loadVocab = async () => {
  try {
    const params = {}
    if (filterLevel.value) params.level = filterLevel.value
    if (searchKeyword.value) params.keyword = searchKeyword.value
    
    const response = await vocabAPI.list(params)
    if (response.data.success) {
      vocabList.value = response.data.data
      selectedIds.value = []
    }
  } catch (error) {
    console.error('获取词库失败', error)
  }
}

const getLevelName = (level) => {
  const levels = { 1: '小学', 2: '初中', 3: '高中' }
  return levels[level] || '未知'
}

const editWord = (word) => {
  editingWord.value = word
  form.value = {
    word: word.word,
    meaning: word.meaning,
    phonetic: word.phonetic || '',
    example: word.example || '',
    level: String(word.level),
    frequency: word.frequency,
    difficulty: word.difficulty
  }
  showAddModal.value = true
}

const deleteWord = async (id) => {
  if (!confirm('确定要删除该单词吗？')) return
  
  try {
    const response = await vocabAPI.delete(id)
    if (response.data.success) {
      loadVocab()
    }
  } catch (error) {
    console.error('删除失败', error)
  }
}

const isAllSelected = computed(() => {
  if (vocabList.value.length === 0) return false
  return vocabList.value.every(w => selectedIds.value.includes(w.id))
})

const toggleAllSelect = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = vocabList.value.map(w => w.id)
  }
}

const selectAllVocab = () => {
  selectedIds.value = vocabList.value.map(w => w.id)
}

const batchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedIds.value.length} 个单词吗？此操作不可撤销。`)) return
  
  try {
    const response = await vocabAPI.batchDelete(selectedIds.value)
    if (response.data.success) {
      alert(response.data.message)
      selectedIds.value = []
      loadVocab()
    }
  } catch (error) {
    alert(error.response?.data?.message || '批量删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingWord.value = null
  form.value = {
    word: '',
    meaning: '',
    phonetic: '',
    example: '',
    level: '2',
    frequency: 3,
    difficulty: 3
  }
}

const saveWord = async () => {
  try {
    if (editingWord.value) {
      await vocabAPI.update(editingWord.value.id, form.value)
    } else {
      await vocabAPI.add(form.value)
    }
    closeModal()
    loadVocab()
  } catch (error) {
    console.error('保存失败', error)
  }
}

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('admin')
  router.push('/admin/login')
}

// ===== 批量上传相关 =====
const showUploadModal = ref(false)
const uploadStep = ref(1)
const selectedFile = ref(null)
const uploading = ref(false)
const importing = ref(false)
const fileInput = ref(null)
const parsedWords = ref([])
const detectedFormat = ref('')
const parsedTotal = ref(0)
const parsedNew = ref(0)
const parsedDup = ref(0)
const showDupOnly = ref(false)
const importResult = ref({ success: 0, skipped: 0 })
const uploadLevel = ref(2)

const filteredPreview = computed(() => {
  if (showDupOnly.value) {
    return parsedWords.value.filter(pw => pw.duplicate)
  }
  return parsedWords.value
})

const selectedCount = computed(() => {
  return parsedWords.value.filter(pw => pw._selected).length
})

const openUpload = () => {
  showUploadModal.value = true
  uploadStep.value = 1
  selectedFile.value = null
  parsedWords.value = []
  uploading.value = false
  importing.value = false
  showDupOnly.value = false
  uploadLevel.value = 2
}

const closeUpload = () => {
  showUploadModal.value = false
}

const closeUploadAndRefresh = () => {
  showUploadModal.value = false
  loadVocab()
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const doUpload = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await vocabAPI.upload(formData)
    if (response.data.success) {
      parsedWords.value = response.data.data.map(pw => ({
        ...pw,
        _selected: !pw.duplicate,
        _edited: false,
        level: uploadLevel.value
      }))
      detectedFormat.value = response.data.detected_format
      parsedTotal.value = response.data.total
      parsedNew.value = response.data.new_count
      parsedDup.value = response.data.duplicate_count
      uploadStep.value = 2
    }
  } catch (error) {
    alert(error.response?.data?.message || '解析失败')
  } finally {
    uploading.value = false
  }
}

const selectAll = () => {
  parsedWords.value.forEach(pw => {
    if (!pw.duplicate) pw._selected = true
  })
}

const deselectAll = () => {
  parsedWords.value.forEach(pw => {
    pw._selected = false
  })
}

const toggleDupOnly = () => {
  showDupOnly.value = !showDupOnly.value
}

const doImport = async () => {
  importing.value = true
  try {
    const selected = parsedWords.value.filter(pw => pw._selected)
    const response = await vocabAPI.importParsed({ words: selected })
    if (response.data.success) {
      importResult.value = {
        success: response.data.message.match(/成功 (\d+)/)?.[1] || selected.length,
        skipped: response.data.message.match(/跳过 (\d+)/)?.[1] || 0
      }
      uploadStep.value = 3
    }
  } catch (error) {
    alert(error.response?.data?.message || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  background: var(--bg-primary);
}

.sidebar {
  width: 250px;
  background: var(--bg-sidebar);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.logo h2 {
  color: var(--text-light);
  font-size: 20px;
  margin: 0 0 32px 0;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: var(--text-light);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-item.active {
  background: var(--accent-gradient);
}

.logout-btn {
  margin-top: auto;
  padding: 12px 16px;
  background: rgba(244, 67, 54, 0.2);
  border: none;
  border-radius: 8px;
  color: #ef9a9a;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(244, 67, 54, 0.3);
}

.main-content {
  flex: 1;
  padding: 32px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 28px;
  color: var(--text-primary);
}

.add-btn {
  padding: 10px 24px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.filter-bar select, .filter-bar input {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-bg);
  color: var(--text-primary);
  border: none;
}

.search-btn {
  padding: 10px 24px;
  background: var(--btn-secondary-bg);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--info-bg);
  border: 1px solid var(--info-color);
  border-radius: 8px;
  margin-bottom: 16px;
}

.batch-info {
  color: var(--info-color);
  font-weight: 600;
  font-size: 14px;
  margin-right: auto;
}

.btn-danger {
  padding: 6px 16px;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-danger:hover {
  background: #d32f2f;
}

.vocab-table {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: var(--table-header-bg);
  font-weight: 600;
  color: var(--text-secondary);
}

.level-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.level-1 { background: var(--level-1-bg); color: var(--level-1-color); }
.level-2 { background: var(--level-2-bg); color: var(--level-2-color); }
.level-3 { background: var(--level-3-bg); color: var(--level-3-color); }

.edit-btn {
  padding: 6px 12px;
  background: var(--info-bg);
  color: var(--info-color);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 8px;
}

.delete-btn {
  padding: 6px 12px;
  background: var(--danger-bg);
  color: var(--danger-color);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: var(--bg-card);
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  color: var(--text-primary);
}

.close-btn {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
}

form {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px 16px;
  border: 2px solid var(--input-border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.form-group textarea {
  min-height: 80px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

/* ===== 批量上传弹窗 ===== */
.header-actions {
  display: flex;
  gap: 12px;
}

.upload-btn {
  padding: 10px 24px;
  background: var(--btn-secondary-bg);
  color: var(--accent-primary);
  border: 2px solid var(--accent-primary);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.upload-btn:hover {
  background: var(--accent-primary);
  color: var(--text-light);
}

.upload-modal .upload-content {
  max-width: 900px;
  width: 95%;
}

.upload-step, .preview-step, .done-step {
  padding: 24px;
}

.level-select-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: 10px;
}

.level-select-row label {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

.level-select {
  padding: 8px 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
}

.level-select:focus {
  border-color: var(--accent-primary);
  outline: none;
}

.level-hint {
  color: var(--text-secondary);
  font-size: 12px;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: var(--accent-primary);
  background: var(--bg-primary);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text {
  color: var(--text-primary);
  font-size: 16px;
  margin-bottom: 8px;
}

.upload-hint {
  color: var(--text-secondary);
  font-size: 13px;
}

.selected-file {
  color: var(--accent-primary);
  font-weight: 600;
  margin-top: 12px;
}

.format-tips {
  background: var(--bg-primary);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 20px;
}

.format-tips h4 {
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 10px;
}

.format-tips ul {
  padding-left: 20px;
  margin-bottom: 10px;
}

.format-tips li {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.8;
}

.format-tips code {
  background: var(--border-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--accent-primary);
}

.tip-note {
  color: var(--info-color);
  font-size: 12px;
}

.upload-actions, .preview-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.upload-actions { justify-content: flex-end; gap: 12px; }

.btn-cancel {
  padding: 10px 24px;
  background: var(--btn-secondary-bg);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.preview-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.summary-badge.success { background: var(--success-bg); color: var(--success-color); }
.summary-badge.info { background: var(--info-bg); color: var(--info-color); }
.summary-badge.new { background: var(--success-bg); color: var(--success-color); }
.summary-badge.dup { background: var(--danger-bg); color: var(--danger-color); }

.summary-right {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 4px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
}

.btn-small:hover {
  background: var(--btn-secondary-bg);
}

.btn-small.btn-warn {
  border-color: #ff9800;
  color: #ff9800;
}

.preview-table-wrapper {
  max-height: 50vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.preview-table th {
  background: var(--table-header-bg);
  color: var(--text-secondary);
  padding: 10px 8px;
  text-align: left;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.preview-table td {
  padding: 8px;
  border-bottom: 1px solid var(--border-color);
}

.row-dup {
  opacity: 0.5;
  background: var(--bg-primary);
}

.inline-edit {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 13px;
}

.inline-edit:focus {
  border-color: var(--accent-primary);
  outline: none;
}

.inline-edit.small {
  width: 50px;
}

.inline-select {
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 13px;
}

.selected-count {
  color: var(--text-secondary);
  font-size: 14px;
  margin-right: 16px;
}

.done-step {
  text-align: center;
  padding: 48px 24px;
}

.done-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.done-step h3 {
  color: var(--text-primary);
  font-size: 20px;
  margin-bottom: 12px;
}

.done-step p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}
</style>