<script setup>
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { onMounted, ref, watch } from 'vue'
import { useMapStore } from '../stores/goodservice'

const mapStore = useMapStore()
mapboxgl.accessToken = 'pk.eyJ1IjoiYXp1cmljZSIsImEiOiJjbGp3NmM5OHkwOWdxM2Vwa2Jjb2tjdzZnIn0.-Ohkio-ahwFWJT3BcckSuA'
let map = null

import { getHeatMapGeoJson } from '@/lib/axios/data'

const enableHeatMap = ref(false)
const enableRoute = ref(true)
const enablePos = ref(true)
let roadLayerAdded = false
let routeIds = []

import { heatmapEntriesHeatId, heatmapEntriesPointId, heatmapEntriesLabelId, updateHeatMap, setHeatmapVisible } from '@/lib/mapbox/heatmap'
import { positionId, updatePosition, setPositionVisible } from '@/lib/mapbox/position'
import { routeId, updateRoute, setRouteVisible } from '@/lib/mapbox/route'

watch(enableHeatMap, (newVal) => { setHeatmapVisible(map, newVal) })
watch(enableRoute, (newVal) => { setRouteVisible(map, newVal) })
watch(enablePos, (newVal) => { setPositionVisible(map, newVal) })

async function updateRoutes() {
  const geojson = await mapStore.getRoutesGeoJson(true)
  console.log('updateRoutes: ', geojson)
  await updateRoute(map, geojson)
}

async function updateTrainPositions() {
  const trainPositionsGeoJson = await mapStore.getTrainPositionsGeoJson()
  await updatePosition(map, trainPositionsGeoJson)
}

const loading = ref(false)
async function allUpdate() {
  console.log('loading...')
  loading.value = true
  try {
    await updateRoutes()
  } catch (error) {
    msg.value = `updateRoutes Failed: ${error}`
    console.error(error)
  }
  try {
    await updateTrainPositions()
  } catch (error) {
    msg.value = `updateTrainPositions Failed: ${error}`
    console.error(error)
  }
  try {
    await updateHeatMap(map)
  } catch (error) {
    msg.value = `updateHeatMap Failed: ${error}`
  }
  map.moveLayer(heatmapEntriesHeatId, positionId)
  map.moveLayer(heatmapEntriesPointId, positionId)
  map.moveLayer(heatmapEntriesLabelId, positionId)
  map.moveLayer(positionId, null)
  loading.value = false
}

async function updateData() {
  loading.value = true
  await mapStore.updateData()
  await updateRoutes()
  loading.value = false
}

const geoControl = new mapboxgl.GeolocateControl({
  positionOptions: {
    enableHighAccuracy: true
  },
  trackUserLocation: true
});

const selectedId = ref('')
const overlay = ref(true)

// 定义起点和终点的坐标
const startPoint = ref(null)
const endPoint = ref(null)

// 定义标记变量
let startMarker = null
let endMarker = null

// 定义起点和终点的输入框
const startLocation = ref('')
const endLocation = ref('')
const selectingStartPoint = ref(false)
const selectingEndPoint = ref(false)

// 监听输入框变化并调用 Geocoding API 获取经纬度
async function fetchCoordinates(location, isStart) {
  if (!location) return

  const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(location)}.json?access_token=${mapboxgl.accessToken}`)
  const data = await response.json()
  const feature = data.features[0]

  if (feature) {
    const coords = feature.geometry.coordinates
    if (isStart) {
      startPoint.value = { lng: coords[0], lat: coords[1] }
    } else {
      endPoint.value = { lng: coords[0], lat: coords[1] }
    }

    updateMarkers()
    if (startPoint.value && endPoint.value) {
      getRoute([startPoint.value.lng, startPoint.value.lat], [endPoint.value.lng, endPoint.value.lat])
    }
  }
}

// 反向地理编码函数
async function reverseGeocode(lngLat, isStart) {
  const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${lngLat.lng},${lngLat.lat}.json?access_token=${mapboxgl.accessToken}`)
  const data = await response.json()
  const feature = data.features[0]

  if (feature) {
    const placeName = feature.place_name
    if (isStart) {
      startLocation.value = placeName
    } else {
      endLocation.value = placeName
    }
  }
}

async function getRoute(start, end) {
  const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${start.join(',')};${end.join(',')}?geometries=geojson&access_token=${mapboxgl.accessToken}`
  const res = await fetch(url)
  const data = await res.json()
  const route = data.routes[0].geometry.coordinates
  console.log('route: ', route)

  const geojson = {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'LineString',
      coordinates: route
    }
  }

  console.log('routeTip', 1)
  if (!roadLayerAdded) {
    map.addSource('road', {
      type: 'geojson',
      data: geojson
    })
    map.addLayer({
      id: 'road',
      type: 'line',
      source: 'road',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#dd0004',
        'line-width': 5,
        'line-opacity': 0.75
      }
    })
    roadLayerAdded = true
  } else {
    map.getSource('road').setData(geojson)
  }
}

watch(startLocation, (newVal) => fetchCoordinates(newVal, true))
watch(endLocation, (newVal) => fetchCoordinates(newVal, false))

function initMap() {
  map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v10',
    maxBounds: [
      [-74.309883, 40.48388],
      [-73.677476, 40.909622]
    ],
    zoom: 9
  })

  map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "bottom-right")
  map.addControl(geoControl, 'bottom-right')

  map.on('load', async () => {
    map.loadImage('train.png', (error, image) => {
      if (error) throw error
      map.addImage('train', image, { 'sdf': true })
    })

    // Stop
    map.addSource('stop', {
      type: 'geojson',
      data: 'stations.geojson'
    })
    map.addLayer({
      id: 'stop',
      type: 'circle',
      source: 'stop',
      paint: {
        'circle-color': '#dddddd',
        'circle-opacity': 0.7,
        'circle-radius': 10
      }
    })

    // Choosing stop
    map.on('click', 'stop', (e) => {
      console.log(`clicked ${e.features[0].properties.id}`)
      selectedId.value = e.features[0].properties.id
    });

    // Cursor changing
    map.on('mouseenter', 'stop', () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'stop', () => {
      map.getCanvas().style.cursor = '';
    });

    // 监听地图点击事件
    map.on('click', (e) => {
      if (selectingStartPoint.value || selectingEndPoint.value) {
        const coords = e.lngLat
        if (selectingStartPoint.value) {
          startPoint.value = { lng: coords.lng, lat: coords.lat }
          reverseGeocode(coords, true)
          selectingStartPoint.value = false
        } else if (selectingEndPoint.value) {
          endPoint.value = { lng: coords.lng, lat: coords.lat }
          reverseGeocode(coords, false)
          selectingEndPoint.value = false
        }

        updateMarkers()
        if (startPoint.value && endPoint.value) {
          getRoute([startPoint.value.lng, startPoint.value.lat], [endPoint.value.lng, endPoint.value.lat])
        }
      }
    })

    await allUpdate()
    setHeatmapVisible(map, enableHeatMap.value)
    overlay.value = false
  })
}

// 更新起点和终点的标记
function updateMarkers() {
  if (startMarker) {
    startMarker.remove()
  }
  if (endMarker) {
    endMarker.remove()
  }

  if (startPoint.value) {
    startMarker = new mapboxgl.Marker()
      .setLngLat(startPoint.value)
      .addTo(map)
  }

  if (endPoint.value) {
    endMarker = new mapboxgl.Marker()
      .setLngLat(endPoint.value)
      .addTo(map)
  }
}

onMounted(initMap)

import StationInfo from '../components/StationInfo.vue'

const autoUpdate = ref(false)
let dataInterval = 0
let trainPosInterval = 0

function switchRealtime(res) {
  if (res) {
    dataInterval = setInterval(updateData, 2500)
    trainPosInterval = setInterval(updateTrainPositions, 100)
  } else {
    clearInterval(dataInterval)
    clearInterval(trainPosInterval)
  }
}

import SnackBar from '@/components/SnackBar.vue'

const msg = ref('')

</script>

<template>
  <SnackBar v-model="msg" />
  <v-overlay :model-value="overlay" class="align-center justify-center" :persistent="true">
    <div class="tw-flex tw-flex-col">
      <v-progress-circular color="white" indeterminate size="64">🫠</v-progress-circular>
      <span class="tw-text-white">loading...</span>
    </div>
  </v-overlay>
  <div class="tw-h-full tw-relative">
    <div class="tw-flex tw-flex-col tw-bg-white
     tw-rounded tw-absolute tw-z-10 tw-m-4 tw-p-4 tw-shadow tw-mb-4 tw-w-1/3 tw-max-w-lg tw-max-h-90">

      <div class="tw-flex tw-items-center">
        <v-btn icon="mdi-refresh" @click="allUpdate" :loading="loading" inline />
        <v-switch label="实时更新" v-model="autoUpdate" @update:modelValue="switchRealtime" class="tw-inline-block tw-ml-4"
          hide-details></v-switch>
      </div>
      <div class="tw-flex tw-items-center">
        <v-switch label="列车位置" v-model="enablePos" class="tw-inline-block tw-ml-4" hide-details></v-switch>
        <v-switch label="线路" v-model="enableRoute" class="tw-inline-block tw-ml-4" hide-details></v-switch>
        <v-switch label="热力图" class="tw-inline-block tw-ml-4" hide-details v-model="enableHeatMap"></v-switch>
      </div>

<hr class="tw-mt-4 tw-mb-4" v-if="selectedId" />

<StationInfo v-model="selectedId" v-if="selectedId" />
    
    <!-- 起点和终点输入框 -->
    <div class="tw-absolute tw-top-10 tw-left-10 tw-bg-white tw-p-2 tw-rounded tw-shadow tw-z-20" style="margin-left: 1200px">
      <label for="start">起点:</label>
      <input type="text" id="start" v-model="startLocation" placeholder="请输入起点名称" />
      <button @click="selectingStartPoint = true">手动选择</button>
      <br />
      <label for="end">终点:</label>
      <input type="text" id="end" v-model="endLocation" placeholder="请输入终点名称" />
      <button @click="selectingEndPoint = true">手动选择</button>
    </div>
    </div>
    <div id="map" class="tw-h-full tw-w-full" />
  </div>
</template>

<style scoped>
.marker {
  background-color: #3fb1ce;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
}
</style>
