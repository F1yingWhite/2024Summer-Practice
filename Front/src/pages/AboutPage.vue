<template>
  <div class="about">
    <div class="con">
      <v-btn icon="mdi-open-in-new" size="large" style="position: fixed;top: 3%;right: 3%; z-index: 3;" @click="exit()" ></v-btn>
      <MTitleVue></MTitleVue>
      <h2 class="green jump">
        <span>我</span>
        <span>又</span>
        <span>会</span>
        <span>生</span>
        <span>产</span>
        <span>阳</span>
        <span>光</span>
        <span>了</span>
      </h2>
      <!-- <h2 class="green ppC">组员有：xyh，cj，zyc，zjn，zjj，zml</h2> -->
    </div>
    <SliderVue style="justify-content: center;width:100%;height: 50%"></SliderVue>
    <div class="image-container">
      <img src="src/assets/xiangrikui.png" style="height: 100px;" />
    </div>
    <CommentColumnVue></CommentColumnVue>
  </div>
  
</template>

<script setup>

import CommentColumnVue from '../components/CommentColumn.vue';
import SliderVue from '../components/Slider.vue';
import MTitleVue from '../components/MTitle.vue';

import { useRouter } from 'vue-router'
const router = useRouter()

function exit(){
  router.push('/login')
}

</script>

<style scope>
html, body {
  width: 100%;  
  height: 100%;
  -webkit-font-smoothing: antialiased;
  display: flex;
  justify-content: center;
  align-items: center;
}

.con{
  text-align: center;
}

h1 {
  font-weight: 500;
  font-size: 2.3rem;
  position: relative;
  top: -10px;
}

h2 {
  font-weight: 500;
  font-size: 1.5rem;
  position: relative;
  top: -10px;
}

.about {
  background-image: url('https://cdn.vuetifyjs.com/images/parallax/material2.jpg');
  text-align: center;
  align-items: center;
  position: absolute;
  background-repeat: repeat-y;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;

  background-size: cover;
  background-position: center;
  background-repeat: repeat-y;

}

.jump {
  height: 60px;
}

.jump span {
  position: relative;
  margin-right: 10px;
  top: 20px;
  display: inline-block;
  animation: bounce .3s ease infinite alternate;
  font-family: 'ChildFont', cursive;
  font-size: 40px;
  color: #FFF;
  text-shadow: 0 1px 0 #CCC,
               0 2px 0 #CCC,
               0 3px 0 #CCC,
               0 4px 0 #CCC,
               0 5px 0 #CCC,
               0 6px 0 transparent,
               0 7px 0 transparent,
               0 8px 0 transparent,
               0 9px 0 transparent,
               0 10px 10px rgba(0, 0, 0, .4);
}

.jump span:nth-child(2) { animation-delay: .1s; }
.jump span:nth-child(3) { animation-delay: .2s; }
.jump span:nth-child(4) { animation-delay: .3s; }
.jump span:nth-child(5) { animation-delay: .4s; }
.jump span:nth-child(6) { animation-delay: .5s; }
.jump span:nth-child(7) { animation-delay: .6s; }
.jump span:nth-child(8) { animation-delay: .7s; }

@keyframes bounce {
  100% {
    top: -20px;
    text-shadow: 0 1px 0 #CCC,
                 0 2px 0 #CCC,
                 0 3px 0 #CCC,
                 0 4px 0 #CCC,
                 0 5px 0 #CCC,
                 0 6px 0 #CCC,
                 0 7px 0 #CCC,
                 0 8px 0 #CCC,
                 0 9px 0 #CCC,
                 0 50px 25px rgba(0, 0, 0, .2);
  }
}

.ppC {
    display: block;
    margin: 0;
    text-align: center;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5), -2px -2px 4px rgba(255, 255, 255, 0.5);
}

.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top:0;
  left: 3%;
}

</style>
