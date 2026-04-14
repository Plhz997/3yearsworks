const { createRouter, createWebHashHistory } = VueRouter

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