<script lang="ts" setup>
import {
  VisXYContainer,
  VisStackedBar,
  VisAxis,
  VisBulletLegend,
  VisTooltip
} from '@unovis/vue';

import { FitMode, Direction, Orientation, StackedBar } from '@unovis/ts';

const props = defineProps<{
  height: number;
  data: any[];

  xAxisTitle: string;
  yAxisTitle: string;

  x: (d: any, i: number) => any;
  y: ((d: any) => any)[];
  tickFormat: (d: any, i: number) => any;
}>();

const { height } = toRefs(props);
const internalHeight = ref(0);
const legendRef = ref<HTMLElement | null>(null);

watch(height, async () => {
  await nextTick();
  console.log('height changed');
  internalHeight.value = height.value - legendRef?.value?.clientHeight || 0;
});

onMounted(async () => {
  await nextTick();

  console.log('legend', getComputedStyle(legendRef.value));
  internalHeight.value = height.value - legendRef?.value?.clientHeight || 0;
  console.log('height', height.value);
  console.log('legend', legendRef?.value?.clientHeight);
});

console.log('TICKFORMAT', props.tickFormat);
</script>

<template>
  <div ref="legendRef">
    <!-- VisBulletLegend
      class="legend"
      style="display: hidden !important"
      :items="chartLabels.map((d) => ({ name: d.legend }))"
    />-->
  </div>
  <VisXYContainer :yDirection="Direction.South" :height="internalHeight">
    <VisStackedBar
      :data="props.data"
      :x="props.x"
      :y="props.y"
      :orientation="Orientation.Horizontal"
    />
    <VisAxis type="x" :label="props.xAxisTitle" />
    <VisAxis
      :label="props.yAxisTitle"
      type="y"
      :tickTextWidth="200"
      :tickTextFitMode="FitMode.Trim"
      :numTicks="props.data.length"
      :tickFormat="props.tickFormat"
    />
  </VisXYContainer>
</template>

<!--<VisTooltip :triggers="{ [StackedBar.selectors.bar]: tooltipTemplate }" />-->
