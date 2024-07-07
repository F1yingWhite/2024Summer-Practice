// 在你的 Pinia store 中
import { defineStore } from 'pinia';
import * as THREE from 'three';

export const useThreeStore = defineStore('three', {
  state: () => ({
    scene: new THREE.Scene(),
    renderer: new THREE.WebGLRenderer(),
  }),
  actions: {
    setScene(newScene) {
      this.scene = newScene;
    },
    setRenderer(newRenderer) {
      this.renderer = newRenderer;
    }
  }
});
