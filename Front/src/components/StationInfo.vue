<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import station_details from '../data/station_details.json';
import { getData } from '../lib/axios/data';
import * as echarts from 'echarts';
import { useRouter } from 'vue-router';

const props = defineProps(['modelValue']);
const emits = defineEmits(['update:modelValue']);

const router = useRouter();

const station = computed(() => station_details[props.modelValue] || {});

let mounted = false;
function updateData() {
  if (myChart) {
    myChart.dispose();
  }
  myChart = echarts.init(chart.value);
  myChart.showLoading();
  getData(props.modelValue).then((res) => {
    myChart.hideLoading();
    myChart.setOption({
      grid: {
        right: 0,
        bottom: 100
      },
      title: {
        text: '人流量图'
      },
      tooltip: {},
      xAxis: {
        data: res.map((v) => v.DateTime.replace(':00:00', '时')),
        axisLabel: {
          rotate: 60
        }
      },
      yAxis: {},
      series: [
        {
          name: '出站人数',
          type: 'line',
          data: res.map((v) => v.Exits)
        },
        {
          name: '入站人数',
          type: 'line',
          data: res.map((v) => v.Entries)
        }
      ]
    });

    // console.log(res[6].DateTime);
    // console.log(res[6].Entries);
    // console.log(res[6].Exits);
    // Save station info to localStorage
    const stationInfo = {
      name: station.value.name,
      id: props.modelValue,
      latitude: station.value.latitude,
      longitude: station.value.longitude,
      borough: station.value.borough,
      dateTime: res[6].DateTime,
      entries: res[6].Entries,
      exits: res[6].Exits
    };
    localStorage.setItem('selectedStation', JSON.stringify(stationInfo));
  });
}

let myChart = null;
const chart = ref(null);
watch(() => props.modelValue, (newValue) => {
  if (newValue && mounted) {
    updateData();
  }
});

onMounted(() => {
  mounted = true;
  updateData();
});

const viewStation = (path) => {
  router.push(path);
};
</script>

<template>
  <div class="tw-flex tw-flex-col tw-items-center tw-flex-1 tw-overflow-y-auto tw-overflow-x-hidden">
    <div class="tw-flex tw-items-center tw-w-full tw-sticky tw-top-0 tw-bg-white tw-z-20 tw-pb-2">
      <v-btn icon="mdi-arrow-left-thin" @click="() => { $emit('update:modelValue', '') }" size="small" />
      <span class="tw-ml-4">{{ station.name }}</span>
      <v-chip class="tw-ml-4">{{ props.modelValue }}</v-chip>
      <v-btn @click="() => viewStation('/SingleSubway')" class="tw-mr-2">查看单站</v-btn>
      <v-btn @click="() => viewStation('/DoubleSubway')">查看双站</v-btn>
    </div>
    <span class="tw-mt-2 tw-mb-2">Longitude: {{ station.longitude }}, Latitude: {{ station.latitude }}</span>
    <div ref="chart" class="tw-w-full tw-mb-5" style="height: 400px;" />
  </div>
</template>
