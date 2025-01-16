<script lang="ts" setup generic="TData, TValue">
import { cn, valueUpdater } from '@/lib/utils';
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

import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';

import { Icon } from '@iconify/vue';

import type {
  ColumnFiltersState,
  SortingState,
  VisibilityState
} from '@tanstack/vue-table';
import {
  FlexRender,
  createColumnHelper,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable
} from '@tanstack/vue-table';

import type { ColumnDef } from '@tanstack/vue-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';

const props = defineProps<{
  title: string | undefined;
  description: string | undefined;

  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  type: any;
}>();

console.log('PROPSDATA', props.data);

const table = useVueTable({
  get data() {
    return props.data;
  },
  get columns() {
    return props.columns;
  },
  getCoreRowModel: getCoreRowModel()
});

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
  <div class="row-span-4 col-span-9 sm:col-span-9 md:col-span-9 h-full">
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
          class="flex-grow flex flex-col items-center justify-center h-full vis-container w-full"
          ref="visContainerRef"
        >
          <Table
            :style="{
              maxHeight: `${contentHeight}px`,
              height: `${contentHeight}px`
            }"
          >
            <TableHeader>
              <TableRow
                v-for="headerGroup in table.getHeaderGroups()"
                :key="headerGroup.id"
              >
                <TableHead
                  v-for="header in headerGroup.headers"
                  :key="header.id"
                >
                  <FlexRender
                    v-if="!header.isPlaceholder"
                    :render="header.column.columnDef.header"
                    :props="header.getContext()"
                  />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <template v-if="table.getRowModel().rows?.length">
                <TableRow
                  v-for="row in table.getRowModel().rows"
                  :key="row.id"
                  :data-state="row.getIsSelected() ? 'selected' : undefined"
                >
                  <TableCell
                    v-for="cell in row.getVisibleCells()"
                    :key="cell.id"
                  >
                    <FlexRender
                      :render="cell.column.columnDef.cell"
                      :props="cell.getContext()"
                    />
                  </TableCell>
                </TableRow>
              </template>
              <template v-else>
                <TableRow>
                  <TableCell :colspan="columns.length" class="h-24 text-center">
                    ...
                  </TableCell>
                </TableRow>
              </template>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
