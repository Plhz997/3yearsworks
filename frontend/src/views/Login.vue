<template>
  <div class="login-container">
    <div class="login-card">
      <h2>用户登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required>
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required>
        </div>
        <button type="submit" class="btn-primary">登录</button>
      </form>
      <p class="link">还没有账号？<a href="/register">立即注册</a></p>
      <p class="link"><a href="/admin/login">管理员登录</a></p>
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
  password: ''
})

const handleLogin = async () => {
  try {
    const response = await authAPI.login(form.value)
    if (response.data.success) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      router.push('/')
    }
  } catch (error) {
    alert(error.response?.data?.message || '登录失败')
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-hero);
  padding: 20px;
}

.login-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-hover);
}

.login-card h2 {
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