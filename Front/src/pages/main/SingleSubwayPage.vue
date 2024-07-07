<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import { useRouter } from 'vue-router';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls';
import { context } from 'three/examples/jsm/nodes/Nodes';

const router = useRouter();
const canvasRef = ref(null);
const stationInfo = ref({});
const showInfoPanel = ref(true);
const loadingProgress = ref(0);
const loadingVisible = ref(true);
let scene, camera, renderer, controls, mixer, clock;
let moveForward = false;
let moveBackward = false;
let moveLeft = false;
let moveRight = false;
let moveUp = false;
let moveDown = false;
let isShiftPressed = false;
const velocity = new THREE.Vector3();
const direction = new THREE.Vector3();
const upDirection = new THREE.Vector3();

function disposeChild(mesh) {
  if (mesh instanceof THREE.Mesh) {
    if (mesh.geometry?.dispose) {
      mesh.geometry.dispose(); // 删除几何体
    }
    if (mesh.material?.dispose) {
      mesh.material.dispose(); // 删除材质
    }
    if (mesh.material?.texture?.dispose) {
      mesh.material.texture.dispose();
    }
  }
  if (mesh instanceof THREE.Group) {
    mesh.clear();
  }
  if (mesh instanceof THREE.Object3D) {
    mesh.clear();
  }
}

function clearThreeScene() {
  if (scene) {
    scene.traverse(item => {
      disposeChild(item);
    });
    THREE.Cache.clear();
    scene.clear();
    if (renderer) {
      renderer.dispose();
      renderer.forceContextLoss();
    }
  }
}



const onKeyDown = (event) => {
  switch (event.code) {
    case 'ArrowUp':
    case 'KeyW':
      moveForward = true;
      break;
    case 'ArrowLeft':
    case 'KeyA':
      moveLeft = true;
      break;
    case 'ArrowDown':
    case 'KeyS':
      moveBackward = true;
      break;
    case 'ArrowRight':
    case 'KeyD':
      moveRight = true;
      break;
    case 'KeyE':
      moveUp = true;
      break;
    case 'KeyQ':
      moveDown = true;
      break;
    case 'ShiftLeft':
    case 'ShiftRight':
      isShiftPressed = true;
      break;
  }
};

const onKeyUp = (event) => {
  switch (event.code) {
    case 'ArrowUp':
    case 'KeyW':
      moveForward = false;
      break;
    case 'ArrowLeft':
    case 'KeyA':
      moveLeft = false;
      break;
    case 'ArrowDown':
    case 'KeyS':
      moveBackward = false;
      break;
    case 'ArrowRight':
    case 'KeyD':
      moveRight = false;
      break;
    case 'KeyE':
      moveUp = false;
      break;
    case 'KeyQ':
      moveDown = false;
      break;
    case 'ShiftLeft':
    case 'ShiftRight':
      isShiftPressed = false;
      break;
  }
};

onMounted(() => {
  // 从LocalStorage读取站点信息
  const storedStationInfo = localStorage.getItem('selectedStation');
  if (storedStationInfo) {
    stationInfo.value = JSON.parse(storedStationInfo);
  }

  // Three.js 初始化代码...
  clock = new THREE.Clock();
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  renderer = new THREE.WebGLRenderer({ antialias: true, canvas: canvasRef.value });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  camera.position.set(3.5, 0.7, -4.8);
  camera.lookAt(3, 0.7, -4.8);
  const axesHelper = new THREE.AxesHelper(5);
  scene.add(axesHelper);

  controls = new PointerLockControls(camera, renderer.domElement);

  document.addEventListener('keydown', onKeyDown);
  document.addEventListener('keyup', onKeyUp);

  renderer.domElement.addEventListener('click', () => {
    controls.lock();
  });

  const rgbeLoader = new RGBELoader();
  rgbeLoader.load('/src/assets/texture/metro_noord_4k.hdr', function (envMap) {
    envMap.mapping = THREE.EquirectangularReflectionMapping;
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

  const loader = new GLTFLoader(loadingManager);
  const modelPath = new URL('/src/assets/model/metro/SingleSubwayStation.glb', import.meta.url).href;

  loader.load(modelPath, function (gltf) {
    scene.add(gltf.scene);

    if (gltf.animations && gltf.animations.length) {
      mixer = new THREE.AnimationMixer(gltf.scene);
      gltf.animations.forEach((clip) => {
        const action = mixer.clipAction(clip);
        action.play();
      });
    }

  }, undefined, function (error) {
    console.error(error);
  });

  function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    if (mixer) mixer.update(delta);

    const speedFactor = isShiftPressed ? 3 : 1;

    if (controls.isLocked === true) {
      direction.z = Number(moveForward) - Number(moveBackward);
      direction.x = Number(moveRight) - Number(moveLeft);
      direction.normalize();

      upDirection.y = Number(moveUp) - Number(moveDown);
      upDirection.normalize();

      if (moveForward || moveBackward) velocity.z -= direction.z * 0.01 * speedFactor;
      if (moveLeft || moveRight) velocity.x -= direction.x * 0.01 * speedFactor;
      if (moveUp || moveDown) velocity.y -= upDirection.y * 0.01 * speedFactor;

      controls.moveRight(-velocity.x);
      controls.moveForward(-velocity.z);
      camera.position.y -= velocity.y;

      velocity.x *= 0.9;
      velocity.z *= 0.9;
      velocity.y *= 0.9;
    }
    renderer.render(scene, camera);
  }

  window.addEventListener('resize', onWindowResize);
});

function onWindowResize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

onBeforeUnmount(() => {
  clearThreeScene();

  document.removeEventListener('keydown', onKeyDown);
  document.removeEventListener('keyup', onKeyUp);
  window.removeEventListener('resize', onWindowResize);

  if (controls) {
    controls.dispose();
  }

  window.location.reload();
});

const toggleInfoPanel = () => {
  showInfoPanel.value = !showInfoPanel.value;
};

const goBack = () => {
  router.push('/');
};

const changeStation = () => {
  router.push('/doubleSubway');
};
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
  <div>
    <div v-if="showInfoPanel" class="info-panel">
      <v-btn @click="goBack">返回</v-btn>
      <v-btn @click="changeStation">切换站点</v-btn>
      <h3>{{ stationInfo.name }}</h3>
      <p>ID: {{ stationInfo.id }}</p>
      <p>经度: {{ stationInfo.longitude }}</p>
      <p>纬度: {{ stationInfo.latitude }}</p>
      <p>所属街区: {{ stationInfo.borough }}</p>
      <p>出站人数: {{ stationInfo.exits }}</p>
      <p>入站人数: {{ stationInfo.entries }}</p>
      <p>日期: {{ stationInfo.dateTime }}</p>
      <v-btn @click="toggleInfoPanel">折叠面板</v-btn>
    </div>
    <div v-else class="info-panel">
      <v-btn @click="toggleInfoPanel">展开面板</v-btn>
    </div>
    <canvas ref="canvasRef" style="width: 100%; height: 100%;"></canvas>
  </div>
</template>

<style>
.info-panel {
  position: fixed;
  bottom: 10px;
  right: 10px;
  background: white;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  z-index: 10;
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
