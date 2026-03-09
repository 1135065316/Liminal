<template>
  <div class="hello">
    <h2>{{ msg }}</h2>
    <button @click="count++">点击次数: {{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  msg: String
})

const count = ref(0)
</script>

<style scoped>
.hello {
  margin-top: 2rem;
}
button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
}
button:hover {
  background: #3aa876;
}
</style>
