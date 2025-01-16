<script setup lang="ts">
import { Scale } from "@unovis/ts";
import {
  VisXYContainer,
  VisLine,
  VisAxis,
  VisCrosshair,
  VisTooltip,
} from "@unovis/vue";

const props = defineProps<{
  height: number;
  data: any;
  count: number;
}>();

const { height, data, count } = toRefs(props);
const refresher = ref(0);

const timeline = computed(() => {
  if (!data.value?.length) return [];

  // Initialize result with dates
  const result = data?.value?.[0]?.timeline?.map((d: any) => ({
    date: d?.date,
    event: d?.event,
  }));

  for (let i = 0; i < result.length; i++) {
    result[i]["average"] = 0;
    result[i]["std_dev"] = 0;

    result[i]["min_multiple"] = Infinity;
    result[i]["max_multiple"] = -Infinity;
    result[i]["avg_multiple"] = 0;

    const totals = [];

    // Collect totals and calculate the sum
    for (let j = 0; j < data.value.length; j++) {
      result[i][`total${j}`] = data.value[j]?.timeline?.[i]?.total || 0;
      totals.push(result[i][`total${j}`]);
      result[i]["average"] += result[i][`total${j}`];
      result[i]["avg_multiple"] +=
        data?.value[j]?.timeline?.[i]?.event?.multiple;

      if (
        result[i]["min_multiple"] >
        data?.value[j]?.timeline?.[i]?.event?.multiple
      ) {
        result[i]["min_multiple"] =
          data?.value[j]?.timeline?.[i]?.event?.multiple;
      }

      if (
        result[i]["max_multiple"] <
        data?.value[j]?.timeline?.[i]?.event?.multiple
      ) {
        result[i]["max_multiple"] =
          data?.value[j]?.timeline?.[i]?.event?.multiple;
      }
    }

    // Calculate the average
    result[i]["average"] /= data.value.length;
    result[i]["avg_multiple"] /= data.value.length;

    // Calculate the standard deviation
    const mean = result[i]["average"];
    result[i]["std_dev"] = Math.sqrt(
      totals.reduce((acc, total) => acc + Math.pow(total - mean, 2), 0) /
        totals.length
    );

    // Compute upper and lower bands
    result[i]["upper_band"] = result[i]["average"] + 2 * result[i]["std_dev"];
    result[i]["lower_band"] = result[i]["average"] - 2 * result[i]["std_dev"];
  }

  return result;
});

const x = (d: any) => new Date(d.date) || [];
const y = computed(() =>
  timeline.value.length
    ? Array.from(
        { length: data.value.length },
        (_, index) => (d: any) => d[`total${index}`]
      )
    : []
);

const yAvg = computed(() =>
  timeline?.value?.length ? (d: any) => d.average : []
);

const yBands = computed(() =>
  timeline?.value?.length
    ? [(d: any) => d.upper_band, (d: any) => d.lower_band]
    : []
);

const xScale = Scale.scaleTime();
const yScale = Scale.scalePow().exponent(0.5);

const internalHeight = ref(0);

watch(height, async () => {
  await nextTick();
  console.log("Height changed");
  internalHeight.value = height.value;
});

watch(timeline, () => {
  refresher.value += 1;
});

onMounted(async () => {
  await nextTick();
  internalHeight.value = height.value;
});

const formatNumber = (value: number) => {
  if (value >= 1e12) {
    return `${(value / 1e12).toFixed(2)}T`;
  } else if (value >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`;
  } else if (value >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`;
  } else if (value >= 1e3) {
    return `${(value / 1e3).toFixed(2)}K`;
  } else {
    return value.toFixed(1);
  }
};

const template = (d: any) => {
  console.log(d);
  const year = d.date.split("-")[0];
  const month = d.date.split("-")[1];
  const day = d.date.split("-")[2];

  const date = new Date();
  date.setFullYear(year);
  date.setMonth(month - 1);
  date.setDate(day);

  return `
  <div class="flex flex-col">
    <div class="flex flex-row items-center">
      <img src="${
        d.event.company.image_url
      }" class="mr-3 h-8 w-8 border rounded-md" />
      <div class="flex flex-col">
        <h1 class="text-md font-bold">${d.event.title}</h1>
        <h5 class="text-sm">${date.toLocaleDateString()}</h5>
      </div>
    </div>

    Action: ${d.event.action}<br/>
    Multiple range: x${d.min_multiple.toFixed(2)} - x${d.max_multiple.toFixed(
    2
  )}<br/>
    Verified: ${d.event.verified ? "Yes" : "No"}<br/>
  </div>

  `;
};
</script>

<template>
  <span>{{ count }}</span>
  <VisXYContainer
    :key="timeline.length"
    :data="timeline"
    :xScale="xScale"
    :yScale="yScale"
    :height="(3 / 4) * internalHeight"
  >
    <VisTooltip />
    <VisCrosshair :template="template" />
    <VisLine
      v-for="(yFn, idx) in y"
      :key="idx"
      :x="x"
      :y="yFn"
      curveType="linear"
      :lineWidth="2"
      :color="`rgba(200, 200, 200, 0.3)`"
    />
    <VisLine
      :x="x"
      :y="yAvg"
      curveType="linear"
      :lineWidth="3"
      :color="`rgba(250, 0, 0, 1)`"
      :lineDashArray="[2]"
      :key="refresher"
    />
    <VisLine
      :x="x"
      :y="yBands[0]"
      curveType="linear"
      :lineWidth="2"
      :color="`rgba(0, 0, 250, 0.3)`"
      :lineDashArray="[2]"
      :key="refresher"
    />
    <VisAxis
      type="x"
      :tickFormat="(value: any) => Intl.DateTimeFormat().format(value)"
      class="rotate-ticks"
    />
    <VisAxis
      type="y"
      :numTicks="5"
      :tickFormat="(value: number) => `$${formatNumber(value)}`"
    />
  </VisXYContainer>
</template>

<style scoped>
/* Select all class that contain tick-label */
tspan.[class*="tick-label"] {
  transform: rotate(45deg);
  text-anchor: end;
}
</style>
