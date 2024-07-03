<script setup>
import { onMounted, ref } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader';

const canvasRef = ref(null);
const loadingProgress = ref(0);
const loadingVisible = ref(true);

onMounted(() => {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );

  const renderer = new THREE.WebGLRenderer({ antialias: true, canvas: canvasRef.value });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // 相机位置
  camera.position.set(0, 5, 10);

  // 世界坐标辅助器
  const axesHelper = new THREE.AxesHelper(5);
  scene.add(axesHelper);

  // 添加轨道控制
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; // 阻尼（惯性），体验更好
  controls.dampingFactor = 0.05;

  // 实例化rgbeLoader
  const rgbeLoader = new RGBELoader();
  rgbeLoader.load('/src/assets/texture/metro_noord_4k.hdr', function (envMap) {
    // 设置球形映射
    envMap.mapping = THREE.EquirectangularReflectionMapping;
    // 设置环境贴图
    scene.background = envMap;
    scene.environment = envMap;
  });

  // 初始化加载管理器
  const loadingManager = new THREE.LoadingManager();
  loadingManager.onStart = function (url, itemsLoaded, itemsTotal) {
    loadingVisible.value = true;
    console.log('开始加载', url, itemsLoaded, itemsTotal);
  };
  loadingManager.onProgress = function (url, itemsLoaded, itemsTotal) {
    loadingProgress.value = (itemsLoaded / itemsTotal) * 100;
    console.log(`加载进度: ${loadingProgress.value}%`);
  };
  loadingManager.onLoad = function () {
    loadingVisible.value = false;
    console.log('加载完成');
    animate();
  };
  loadingManager.onError = function (url) {
    console.error('加载出错', url);
  };

  // 加载 gltf 模型
  const loader = new GLTFLoader(loadingManager);
  const modelPath = new URL('/src/assets/model/metro/SubwayStation.glb', import.meta.url).href;
  
  // // 加载 draco 压缩模型
  // const dracoLoader = new DRACOLoader();
  // dracoLoader.setDecoderPath('/public/draco/');
  // loader.setDRACOLoader(dracoLoader);
  
  loader.load(modelPath, function (gltf) {
    // 设置位置
    // gltf.scene.position.set(-14, 10, 14);
    // 添加到场景
    scene.add(gltf.scene);
  }, undefined, function (error) {
    console.error(error);
  });

  // 渲染循环
  function animate() {
    requestAnimationFrame(animate);
    controls.update(); // 更新控制器
    renderer.render(scene, camera);
  }

  // 窗口大小调整
  window.addEventListener('resize', () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  });
});
</script>

<template>
  <div v-if="loadingVisible" class="loading-screen">
    <div class="progress-circle">
      <div class="progress-circle-inner"
        :style="{ background: 'conic-gradient(#00ff00 ' + loadingProgress + '%, #000000 ' + loadingProgress + '%)' }">
      </div>
      <div class="progress-circle-text">{{ loadingProgress.toFixed(2) }}%</div>
    </div>
  </div>
  <canvas ref="canvasRef"></canvas>
</template>

<style>
canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 24px;
  z-index: 1000;
}

.progress-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #000000;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.progress-circle-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.progress-circle-text {
  position: absolute;
  color: white;
  font-size: 16px;
  font-weight: bold;
}
</style>
