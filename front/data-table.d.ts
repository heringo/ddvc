import '@tanstack/vue-table';

declare module '@tanstack/vue-table' {
  interface ColumnMeta {
    headerClassName?: string;
    cellClassName?: string;
  }
}
