<script setup>
import router from '../router/index'
import { ref } from 'vue'
import {logout} from '../lib/axios/admin'
import { useTokenStore } from '../stores/token'
const tokenStore = useTokenStore()

const donateDialog = ref(false)

//exit
function onLogout() {
  tokenStore.unSetToken()
  tokenStore.unSetPermission()
  logout().then(() => {
    console.log('logout')
  }).catch((err) => {
    console.log(err)
  })
  router.push('/login')
}

</script>

<template>
  <v-app-bar class="bar" :elevation="2"  image="src/assets/NavigationBar2.png" >
    <v-app-bar-nav-icon  @click="() => { router.push('/about') }">
      <img src="src/assets/NavigationBar-icon.png" alt="Custom Icon">
    </v-app-bar-nav-icon>
    <!-- fire-circle -->
    <v-toolbar-title>大苹果交通</v-toolbar-title>
    <v-btn icon="mdi-bell-alert" @click="()=>{router.push('/warning')}" v-if="tokenStore.isGov()"></v-btn>
    <v-btn icon="mdi-map-search" @click="()=>{router.push('/')}"></v-btn>
    <!-- 添加问答页面按钮 -->
    <v-btn icon="mdi-comment-question-outline" @click="()=>{router.push('/question')}"></v-btn>
    <v-btn icon="mdi-currency-usd" @click="() => { donateDialog = true }" />
    <v-btn class="tw-text-purple" icon="mdi-wrench" v-if="tokenStore.isAdmin()" @click="() => { router.push('/admin') }"></v-btn>
    <v-btn icon="mdi-poll" @click="() => { router.push('/count') }"></v-btn>
    <v-btn icon="mdi-exit-run" @click="onLogout()"></v-btn>
  </v-app-bar>
</template>

<style scoped>
</style>

