<template>
  <div class="container">
    <h1>🔍 Buscar Operadora</h1>
    <input
      type="text"
      v-model="termo"
      @input="buscar"
      placeholder="Digite o nome da operadora..."
    />
    <ul v-if="resultados.length">
      <li v-for="item in resultados" :key="item.registro_operadora">
        <strong>{{ item.razao_social }}</strong> ({{ item.registro_operadora }})
      </li>
    </ul>
    <p v-else-if="termo">Nenhum resultado encontrado.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const termo = ref('')
const resultados = ref([])

const buscar = async () => {
  if (termo.value.length < 3) {
    resultados.value = []
    return
  }

  try {
    const { data } = await axios.get(`http://127.0.0.1:8000/operadoras?q=${termo.value}`)
    resultados.value = data.resultados
  } catch (err) {
    console.error('Erro ao buscar operadoras:', err)
    resultados.value = []
  }
}
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 2rem auto;
  font-family: sans-serif;
}
input {
  padding: 0.5rem;
  width: 100%;
  font-size: 1rem;
  margin-bottom: 1rem;
}
</style>
