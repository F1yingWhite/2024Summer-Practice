import * as THREE from 'three';

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

export { disposeChild };
