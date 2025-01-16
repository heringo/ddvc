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
  <div class="row-span-2 col-span-1 sm:col-span-2 md:col-span-3 h-full">
    <Card class="min-h-full min-w-full h-full flex flex-col">
      <CardHeader>
        <CardTitle class="break-all">Histogram</CardTitle>
        <CardDescription class="break-all">Blablblablabla</CardDescription>
      </CardHeader>
      <CardContent
        class="flex-grow flex flex-col items-center justify-center h-full"
      >
        <div
          ref="visContainerRef"
          class="flex-grow flex flex-col items-center justify-center h-full vis-container w-full"
        >
          <AppChartsHistogram
            v-if="contentHeight"
            :style="{ height: `${contentHeight}px` }"
            :height="contentHeight"
          />
        </div>
      </CardContent>
    </Card>
  </div>
</template>
