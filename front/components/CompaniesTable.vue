<script setup lang="ts">
import { Icon } from "@iconify/vue";
import type {
  ColumnDef,
  ColumnFiltersState,
  ExpandedState,
  SortingState,
  VisibilityState,
} from "@tanstack/vue-table";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { valueUpdater } from "@/lib/utils";
import {
  FlexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
} from "@tanstack/vue-table";
import { ArrowUpDown, ChevronDown } from "lucide-vue-next";
import { h, ref } from "vue";

export interface Payment {
  id: string;
  amount: number;
  status: "pending" | "processing" | "success" | "failed";
  email: string;
}

const formatAmount = (amount: number) => {
  let formattedAmount = amount.toString();
  let unit = "";

  if (amount < 1000000) {
    formattedAmount = (amount / 1000).toFixed(1);
    unit = "K";
  } else if (amount < 1000000000) {
    formattedAmount = (amount / 1000000).toFixed(1);
    unit = "M";
  } else {
    formattedAmount = (amount / 1000000000).toFixed(1);
    unit = "B";
  }

  return `${formattedAmount}${unit}`;
};

const formatFunding = (funding: any) => {
  if (!funding) {
    return "Unknown";
  }

  // want to keep the '-' in pre-seed
  else if (funding === "PRE_SEED") {
    return "Pre-seed";
  }

  return funding
    .split("_")
    .map((word: string) => word[0] + word.slice(1).toLowerCase())
    .join(" ");
};

const props = defineProps<{
  data: any;
}>();

const data = props.data as any;

const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "logo_url",
    header: () => h("div", { class: "w-8" }, ""),
    cell: ({ row }) =>
      h("img", {
        src: row.getValue("logo_url"),
        class: "h-8 w-8 border rounded-full",
      }),
  },

  {
    accessorKey: "domain",
    header: "Name",
    cell: ({ row }) =>
      h(
        "a",
        { href: `https://${row.getValue("domain")}`, target: "_blank" },
        (row as any)?.original?.name
      ),
  },
  {
    accessorKey: "topic_probability",
    header: ({ column }) => {
      return h(
        Button,
        {
          variant: "ghost",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        },
        () => [
          "Confidence",
          h(Icon, {
            class: "ml-2 h-4 w-4",
            icon:
              column.getIsSorted() === "asc"
                ? "lucide:arrow-up"
                : column.getIsSorted() === "desc"
                ? "lucide:arrow-down"
                : "lucide:text",
          }),
        ]
      );
    },
    cell: ({ row }) => {
      const probability: any = row.getValue("topic_probability");

      let color = "red";
      let confidence = "Low";

      if (probability >= 0.8) {
        color = "bg-green-300";
        confidence = "High";
      } else if (probability >= 0.5) {
        color = "bg-orange-300";
        confidence = "Medium";
      } else {
        color = "bg-red-300";
        confidence = "Low";
      }

      return h(
        "div",
        { class: `${color} rounded-xl p-1 text-center` },
        confidence
      );
    },
  },
  {
    accessorKey: "founded_at",
    header: ({ column }) => {
      return h(
        Button,
        {
          variant: "ghost",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        },
        () => [
          "Founding Year",
          h(Icon, {
            class: "ml-2 h-4 w-4",
            icon:
              column.getIsSorted() === "asc"
                ? "lucide:arrow-up"
                : column.getIsSorted() === "desc"
                ? "lucide:arrow-down"
                : "lucide:text",
          }),
        ]
      );
    },
    cell: ({ row }) => {
      const foundedAt: any = row.getValue("founded_at");
      const foundingYear = new Date(foundedAt).getFullYear();

      return h("div", { class: "capitalize" }, foundingYear);
    },
  },
  {
    accessorKey: "headcount",
    header: ({ column }) => {
      return h(
        Button,
        {
          variant: "ghost",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        },
        () => [
          "Headcount",
          h(Icon, {
            class: "ml-2 h-4 w-4",
            icon:
              column.getIsSorted() === "asc"
                ? "lucide:arrow-up"
                : column.getIsSorted() === "desc"
                ? "lucide:arrow-down"
                : "lucide:text",
          }),
        ]
      );
    },
    cell: ({ row }) =>
      h("div", { class: "capitalize" }, row.getValue("headcount")),
  },
  {
    accessorKey: "funding_total",
    header: ({ column }) => {
      return h(
        Button,
        {
          variant: "ghost",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        },
        () => [
          "Total funding",
          h(Icon, {
            class: "ml-2 h-4 w-4",
            icon:
              column.getIsSorted() === "asc"
                ? "lucide:arrow-up"
                : column.getIsSorted() === "desc"
                ? "lucide:arrow-down"
                : "lucide:text",
          }),
        ]
      );
    },

    cell: ({ row }) => {
      const formattedAmount = formatAmount(row.getValue("funding_total"));
      return h("div", { class: "capitalize" }, `${formattedAmount}`);
    },
  },
  /*
  country*/
  {
    accessorKey: "funding_stage",
    header: "Funding stage",
    cell: ({ row }) => {
      const formattedStage = formatFunding(row.getValue("funding_stage"));
      return h("div", { class: "capitalize" }, `${formattedStage}`);
    },
  },
  {
    accessorKey: "country",
    header: "Country",
    cell: ({ row }) =>
      h("div", { class: "capitalize" }, row.getValue("country")),
  },
];

const sorting = ref<SortingState>([]);
const columnFilters = ref<ColumnFiltersState>([]);
const columnVisibility = ref<VisibilityState>({});
const rowSelection = ref({});
const expanded = ref<ExpandedState>({});

const table = useVueTable({
  data,
  columns,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  onSortingChange: (updaterOrValue) => valueUpdater(updaterOrValue, sorting),
  onColumnFiltersChange: (updaterOrValue) =>
    valueUpdater(updaterOrValue, columnFilters),
  onColumnVisibilityChange: (updaterOrValue) =>
    valueUpdater(updaterOrValue, columnVisibility),
  onRowSelectionChange: (updaterOrValue) =>
    valueUpdater(updaterOrValue, rowSelection),
  onExpandedChange: (updaterOrValue) => valueUpdater(updaterOrValue, expanded),
  state: {
    get sorting() {
      return sorting.value;
    },
    get columnFilters() {
      return columnFilters.value;
    },
    get columnVisibility() {
      return columnVisibility.value;
    },
    get rowSelection() {
      return rowSelection.value;
    },
    get expanded() {
      return expanded.value;
    },
  },
});
</script>

<template>
  <div class="w-full">
    <div class="black-shadow pt-1" id="companies-table">
      <Table>
        <TableHeader>
          <TableRow
            v-for="headerGroup in table.getHeaderGroups()"
            :key="headerGroup.id"
          >
            <TableHead v-for="header in headerGroup.headers" :key="header.id">
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
            <template v-for="row in table.getRowModel().rows" :key="row.id">
              <TableRow :data-state="row.getIsSelected() && 'selected'">
                <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                  <FlexRender
                    :render="cell.column.columnDef.cell"
                    :props="cell.getContext()"
                  />
                </TableCell>
              </TableRow>
              <TableRow v-if="row.getIsExpanded()">
                <TableCell :colspan="row.getAllCells().length">
                  {{ JSON.stringify(row.original) }}
                </TableCell>
              </TableRow>
            </template>
          </template>

          <TableRow v-else>
            <TableCell :colspan="columns.length" class="h-24 text-center">
              No results.
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <div class="flex items-center justify-end space-x-2 py-4">
      <div class="space-x-2">
        <Button
          variant="outline"
          size="sm"
          class="black-shadow with-hover"
          :disabled="!table.getCanPreviousPage()"
          @click="table.previousPage()"
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          :disabled="!table.getCanNextPage()"
          @click="table.nextPage()"
          class="black-shadow with-hover"
        >
          Next
        </Button>
      </div>
    </div>
  </div>
</template>
