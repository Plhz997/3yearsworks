<template>
  <div class="register-container">
    <div class="register-card">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required>
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required>
        </div>
        <div class="form-group">
          <label>邮箱（可选）</label>
          <input v-model="form.email" type="email" placeholder="请输入邮箱">
        </div>
        <button type="submit" class="btn-primary">注册</button>
      </form>
      <p class="link">已有账号？<a href="/login">立即登录</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../utils/api'

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  email: ''
})

const handleRegister = async () => {
  try {
    const response = await authAPI.register(form.value)
    if (response.data.success) {
      alert('注册成功，请登录')
      router.push('/login')
    }
  } catch (error) {
    alert(error.response?.data?.message || '注册失败')
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-hero);
  padding: 20px;
}

.register-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-hover);
}

.register-card h2 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 32px;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--input-border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-bg);
  color: var(--text-primary);
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.btn-primary {
  width: 100%;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-text);
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.link {
  text-align: center;
  margin-top: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.link a {
  color: var(--accent-primary);
  text-decoration: none;
}

.link a:hover {
  text-decoration: underline;
}
</style>