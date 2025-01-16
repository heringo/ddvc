<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import { useResizeObserver } from '@vueuse/core';

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';

import { cn } from '@/lib/utils';

const contentHeight = ref(0);
const visContainerRef = ref<HTMLElement | null>(null);

const props = defineProps<{
  title: string | undefined;
  description: string | undefined;
  data: any[];

  xAxisTitle: string;
  yAxisTitle: string;

  x: (d: any, i: number) => any;
  y: ((d: any) => any)[];
  tickFormat: (d: any, i: number) => any;
}>();

const getHeight = async () => {
  if (visContainerRef.value) {
    contentHeight.value = 0;
    await nextTick();

    // Measure the height excluding padding, border, and margin
    const computedStyle = getComputedStyle(visContainerRef.value);

    const height =
      visContainerRef.value.clientHeight -
      parseFloat(computedStyle.paddingTop) -
      parseFloat(computedStyle.paddingBottom);
    contentHeight.value = height;

    return height;
  }

  return 0;
};

onMounted(async () => {
  await getHeight();
});

// on resize recalculate height
useResizeObserver(visContainerRef, async () => {
  await getHeight();
});
</script>

<template>
  <div class="row-span-2 col-span-9 sm:col-span-9 md:col-span-9 h-full">
    <Card class="min-h-full min-w-full h-full flex flex-col">
      <CardHeader>
        <CardTitle v-if="props?.title?.length">{{ props.title }}</CardTitle>
        <CardDescription v-if="props?.description?.length">
          {{ props.description }}
        </CardDescription>
      </CardHeader>
      <CardContent
        class="flex-grow flex flex-col items-center justify-center h-full"
      >
        <div
          ref="visContainerRef"
          class="flex-grow flex flex-col items-center justify-center h-full vis-container w-full"
        >
          <AppChartsBars
            v-if="contentHeight"
            :style="{ height: `${contentHeight}px` }"
            :height="contentHeight"
            :data="props.data"
            :x="props.x"
            :y="props.y"
            :xAxisTitle="props.xAxisTitle"
            :yAxisTitle="props.yAxisTitle"
            :tickFormat="props.tickFormat"
          />
        </div>
      </CardContent>
    </Card>
  </div>
</template>
