<script setup lang="ts">
import {
  VisXYContainer,
  VisGroupedBar,
  VisAxis,
  VisBulletLegend
} from '@unovis/vue';

type DataPoint = {
  x: number;
  y: number;
};

const colors = {
  y: 'gray'
};

const data: DataPoint[] = [
  {
    x: -10,
    y: 6505863
  },
  {
    x: -9,
    y: 811015
  },
  {
    x: -8,
    y: 817798
  },
  {
    x: -7,
    y: 20663272
  },
  {
    x: -6,
    y: 9625419
  },
  {
    x: -5,
    y: 4071625
  },
  {
    x: -4,
    y: 1212870
  },
  {
    x: -3,
    y: 510456
  },
  {
    x: -2,
    y: 1501463
  },
  {
    x: -1,
    y: 4292059
  },
  {
    x: 0,
    y: 1246094
  },
  {
    x: 1,
    y: 6505863
  },
  {
    x: 2,
    y: 811015
  },
  {
    x: 3,
    y: 817798
  },
  {
    x: 4,
    y: 20663272
  },
  {
    x: 5,
    y: 9625419
  },
  {
    x: 6,
    y: 4071625
  },
  {
    x: 7,
    y: 1212870
  },
  {
    x: 8,
    y: 510456
  },
  {
    x: 9,
    y: 1501463
  },
  {
    x: 10,
    y: 4292059
  }
];

const items = Object.entries(colors).map(([n, c]) => ({
  name: n.toUpperCase(),
  color: c
}));
const x = (d: DataPoint) => d.x;
const y = [(d: DataPoint) => d.y];
const color = (d: DataPoint, i: number) => items[i].color;

const props = defineProps<{
  height: number;
}>();

const { height } = toRefs(props);
const internalHeight = ref(0);

watch(height, async () => {
  await nextTick();
  internalHeight.value = height.value;
});

onMounted(async () => {
  await nextTick();
  internalHeight.value = height.value;
});
</script>

<template>
  <VisXYContainer :height="internalHeight">
    <VisGroupedBar
      :data="data"
      :x="x"
      :y="y"
      :color="color"
      :roundedCorners="true"
    />
    <!--label="Score"
        -->
    <VisAxis type="x" :numTicks="5" :tickFormat="(value) => value.toString()" />
    <VisAxis type="y" :tickFormat="(value) => `${value / 10 ** 6}%`" />
  </VisXYContainer>
</template>
