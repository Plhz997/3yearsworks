import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import TestStart from '../views/TestStart.vue'
import Test from '../views/Test.vue'
import TestResult from '../views/TestResult.vue'
import History from '../views/History.vue'
import WrongWords from '../views/WrongWords.vue'
import Profile from '../views/Profile.vue'
import AdminLogin from '../views/admin/AdminLogin.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminVocab from '../views/admin/AdminVocab.vue'
import AdminRecords from '../views/admin/AdminRecords.vue'
import AdminStats from '../views/admin/AdminStats.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/test/start', name: 'TestStart', component: TestStart },
  { path: '/test', name: 'Test', component: Test },
  { path: '/test/result', name: 'TestResult', component: TestResult },
  { path: '/history', name: 'History', component: History },
  { path: '/wrong-words', name: 'WrongWords', component: WrongWords },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/admin/users', name: 'AdminUsers', component: AdminUsers },
  { path: '/admin/vocab', name: 'AdminVocab', component: AdminVocab },
  { path: '/admin/records', name: 'AdminRecords', component: AdminRecords },
  { path: '/admin/stats', name: 'AdminStats', component: AdminStats }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
