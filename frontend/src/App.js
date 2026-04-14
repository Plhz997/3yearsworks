const { createApp } = Vue

const app = createApp({
  template: `<router-view />`
})

app.use(router)
app.use(ElementPlus)
app.mount('#app')