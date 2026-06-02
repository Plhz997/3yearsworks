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
          <select v-model="uploadLevel" class="upload-level">
            <option value="1">上传到小学</option>
            <option value="2">上传到初中</option>
            <option value="3">上传到高中</option>
          </select>
          <label class="upload-btn">
            <span>📤 批量上传</span>
            <input type="file" accept=".csv,.txt" @change="handleFileUpload" style="display: none;">
          </label>
          <button @click="batchDeleteWords" :disabled="selectedIds.length === 0" class="batch-delete-btn">
            批量删除 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
          </button>
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
      
      <div class="vocab-table">
        <table>
          <thead>
            <tr>
              <th>
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll">
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
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { vocabAPI } from '../../utils/api'

const router = useRouter()

const vocabList = ref([])
const selectedIds = ref([])
const filterLevel = ref('')
const uploadLevel = ref('2')
const searchKeyword = ref('')
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

const isAllSelected = computed(() => {
  return vocabList.value.length > 0 && selectedIds.value.length === vocabList.value.length
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
      selectedIds.value = selectedIds.value.filter(id => vocabList.value.some(word => word.id === id))
    }
  } catch (error) {
    console.error('获取词库失败', error)
  }
}

const toggleSelectAll = (event) => {
  selectedIds.value = event.target.checked ? vocabList.value.map(word => word.id) : []
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

const batchDeleteWords = async () => {
  if (selectedIds.value.length === 0) return
  if (!confirm(`确定要批量删除选中的 ${selectedIds.value.length} 个单词吗？此操作不可恢复。`)) return

  try {
    const response = await vocabAPI.batchDelete(selectedIds.value)
    if (response.data.success) {
      alert(response.data.message)
      selectedIds.value = []
      loadVocab()
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '批量删除失败'
    alert(errorMsg)
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

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (!confirm(`确定要上传文件 "${file.name}" 到「${getLevelName(parseInt(uploadLevel.value))}」词库吗？\n\n提示：如果文件第3列填写了学段，会优先使用文件里的学段。`)) {
    event.target.value = ''
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('level', uploadLevel.value)
  
  try {
    const response = await vocabAPI.upload(formData)
    if (response.data.success) {
      alert(response.data.message)
      loadVocab()
    } else {
      alert('上传失败：' + response.data.message)
    }
  } catch (error) {
    console.error('上传失败', error)
    const errorMsg = error.response?.data?.message || error.response?.data?.msg || error.message || '未知错误'
    console.log('Error details:', error.response?.data)
    alert('上传失败：' + errorMsg + '\n\n详情请查看控制台 (F12)')
  }
  
  event.target.value = ''
}

const goTo = (path) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('admin')
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  background: #f5f7fa;
}

.sidebar {
  width: 250px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.logo h2 {
  color: white;
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
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: #333;
}

.add-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.upload-level {
  padding: 10px 14px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  background: white;
  color: #333;
}

.upload-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(17, 153, 142, 0.4);
}

.batch-delete-btn {
  padding: 10px 18px;
  background: linear-gradient(135deg, #ff5f6d 0%, #ffc371 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.batch-delete-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.batch-delete-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 95, 109, 0.35);
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.filter-bar select, .filter-bar input {
  padding: 10px 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
}

.search-btn {
  padding: 10px 24px;
  background: #f5f7fa;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
}

.vocab-table {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e4e7ed;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #666;
}

.level-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.level-1 { background: #e8f5e9; color: #2e7d32; }
.level-2 { background: #fff3e0; color: #e65100; }
.level-3 { background: #fce4ec; color: #c2185b; }

.edit-btn {
  padding: 6px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 8px;
}

.delete-btn {
  padding: 6px 12px;
  background: #ffebee;
  color: #f44336;
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
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
  border-bottom: 1px solid #e4e7ed;
}

.modal-header h3 {
  font-size: 18px;
  color: #333;
}

.close-btn {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
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
  color: #666;
  font-size: 14px;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 80px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}
</style>
