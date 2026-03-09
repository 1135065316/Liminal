<template>
  <div class="app">
    <h1>🚀 Vue3 + JS 前端</h1>
    <p>端口: 14514</p>
    <p>状态: <span class="status">运行中</span></p>
    <HelloWorld msg="欢迎使用 Vue3" />
  </div>
</template>

<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<style scoped>
.app {
  text-align: center;
  padding: 2rem;
  font-family: 'Microsoft YaHei', sans-serif;
}
.status {
  color: #42b883;
  font-weight: bold;
}
h1 {
  color: #35495e;
}
</style>
