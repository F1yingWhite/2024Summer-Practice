<script setup>
    import * as THREE from 'three'
    // 导入轨道控制器
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    // 导入lil-gui
    import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js' 

    // 创建场景
    const scene = new THREE.Scene();

    // 创建相机
    const camera = new THREE.PerspectiveCamera(
        45, // 视角
        window.innerWidth / window.innerHeight, // 宽高比
        0.1, // 近平面
        1000 // 远平面
    )

    // 创建渲染器
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // 创建几何体
    const geometry = new THREE.BufferGeometry();
    const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
    // // 使用坐标绘制
    // const vertices = new Float32Array([
    //     0, 0, 0,
    //     1, 0, 0,
    //     0, 1, 0,

    //     1, 1, 0,
    //     0, 1, 0,
    //     1, 0, 0,
    // ]);
    // // 设置几何体的顶点位置
    // geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    // 使用索引绘制
    const vertices = new Float32Array([
        0, 0, 0,
        1, 0, 0,
        0, 1, 0,
        1, 1, 0,
    ]);
    // 设置几何体的顶点位置
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    // 设置几何体的顶点索引
    const indexes = new Uint16Array([
        0, 1, 2,
        1, 3, 2,
    ])
    // 设置索引实现共用顶点
    geometry.setIndex(new THREE.BufferAttribute(indexes, 1));
    // 设置两个顶点组，形成两个材质
    geometry.addGroup(0, 3, 0);
    geometry.addGroup(3, 3, 1);

    // 创建材质
    // 父元素材质
    const parentMaterial0 = new THREE.MeshBasicMaterial({
        color: 0xff0000,
        // wireframe: true,
    });
    const parentMaterial1 = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        // wireframe: true,
    });
    const parentMaterial2 = new THREE.MeshBasicMaterial({
        color: 0x0000ff,
        // wireframe: true,
    });
    const parentMaterial3 = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        // wireframe: true,
    });
    const parentMaterial4 = new THREE.MeshBasicMaterial({
        color: 0xff00ff,
        // wireframe: true,
    });
    const parentMaterial5 = new THREE.MeshBasicMaterial({
        color: 0xffff00,
        // wireframe: true,
    });
    const parentMaterial6 = new THREE.MeshBasicMaterial({
            color: 0xffffff,
            // wireframe: true,
    });

    // 子元素材质
    const material = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        side: THREE.DoubleSide,
        wireframe: true,
    });
    const material1 = new THREE.MeshBasicMaterial({
        color: 0x0000ff,
        side: THREE.DoubleSide,
        // wireframe: true,
    });

    // 创建网格
    let parentCube = new THREE.Mesh(cubeGeometry, [
        parentMaterial0, 
        parentMaterial1, 
        parentMaterial2, 
        parentMaterial3, 
        parentMaterial4, 
        parentMaterial5, 
        parentMaterial6
    ]);
    const cube = new THREE.Mesh(geometry, [material, material1]);
    parentCube.add(cube);
    parentCube.position.set(-3, 0, 0)

    // cube.position.x = 2;
    cube.position.set(3, 0, 0);
    // 设置立方体的放大
    cube.scale.set(2, 2, 2);
    // 绕着x轴旋转
    // cube.rotation.set(Math.PI / 4, 0, 0, 'XYZ');
    // 添加到场景中
    scene.add(parentCube);

    // 设置相机位置
    camera.position.z = 5;
    camera.position.y = 2;
    camera.position.x = 2;
    camera.lookAt(0, 0, 0);

    // 添加世界坐标辅助器
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    // 添加轨道控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    // 设置带阻尼的惯性
    controls.enableDamping = true;
    // 设置阻尼系数
    controls.dampingFactor = 0.05;
    // // 设置自动旋转
    // controls.autoRotate = true;
    // // 设置自动旋转速度
    // controls.autoRotateSpeed = 1;
    // // 设置相机距离原点的最远距离
    // controls.minDistance = 2;
    // // 设置相机距离原点的最远距离
    // controls.maxDistance = 10;

    // 渲染函数
    function animate() {
        controls.update();
        requestAnimationFrame(animate);
        // 旋转
        // cube.rotation.x += 0.01;
        // cube.rotation.y += 0.01;
        // 渲染
        renderer.render(scene, camera);
    }
    animate();

    // 监听窗口变化
    window.addEventListener('resize', () => {
        // 更新摄像头宽高比
        camera.aspect = window.innerWidth / window.innerHeight;
        // 更新摄像机的投影矩阵
        camera.updateProjectionMatrix();
        // 更新渲染器宽高比
        renderer.setSize(window.innerWidth, window.innerHeight);
        // 设置渲染器的像素比
        renderer.setPixelRatio(window.devicePixelRatio);
    });

    let eventObj = {
        Fullscreen: function () {
            // 全屏
            document.body.requestFullscreen();
            console.log("全屏")
        },

        ExitFullscreen: function () {
            // 退出全屏
            document.exitFullscreen();
            console.log("退出全屏")
        },
    }

    // 创建GUI
    const gui = new GUI();
    // 添加按钮
    gui.add(eventObj, "Fullscreen").name("全屏");
    gui.add(eventObj, "ExitFullscreen").name("退出全屏");
    // 控制立方体的位置
    let folder = gui.addFolder("立方体位置");
    folder.open();
    folder.add(cube.position, "x").min(-10).max(10).step(1).name("移动x");
    folder.add(cube.position, "y").min(-10).max(10).step(1).name("移动y");
    folder.add(cube.position, "z").min(-10).max(10).step(1).name("移动z");
    // 控制立方体的缩放
    gui.add(cube.scale, "x", 0, 10).name("缩放x");
    // 切换父元素线框模式
    gui.add(parentMaterial, "wireframe").name("父元素线框模式");

    let colorParams = {
        cubeColor: "#00ff00",
    }
    gui.addColor(colorParams, "cubeColor").name("立方体颜色").onChange((val) => {
        cube.material.color.set(val);
    });


</script>

<template>
    <div>
    </div>
</template>

<style>


</style>