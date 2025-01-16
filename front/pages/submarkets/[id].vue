<script lang="ts" setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

import CompaniesTable from "@/components/CompaniesTable.vue";

const router = useRouter();
const supabase: any = useSupabaseClient();

const submarket = ref();
const companies = ref();

const { id } = useRoute().params;

// Fetch companies data
const {
  data: companiesData,
  error: companiesError,
}: { data: any; error: any } = await useAsyncData(() =>
  supabase.from("companies").select("*").eq("topic_id", id)
);

// Fetch submarket data
const {
  data: submarketData,
  error: submarketError,
}: { data: any; error: any } = await useAsyncData(() =>
  supabase.from("submarkets").select("*").eq("id", id).single()
);

submarket.value = submarketData?.value?.data;
companies.value = companiesData?.value?.data?.sort(
  (a: any, b: any) => b.funding_amount - a.funding_amount
);
</script>

<template>
  <div class="container min-h-screen flex flex-row py-12 justify-center">
    <div class="text-justify w-full sm:w-2/3 xl:w-1/2">
      <NuxtLink to="/" class="flex flex-row items-center mb-2">
        <Logo class="w-4 h-4 mr-1" />
        <h1 class="text-xl font-bold">Pulse</h1>
      </NuxtLink>
      <h1 class="text-4xl text-left font-bold mb-4">
        {{ submarket?.topic_name }}
      </h1>
      <p class="text-gray-500 mb-8">
        {{ submarket?.topic_description }}
      </p>

      <h3 class="text-2xl font-bold mb-4">Companies</h3>
      <CompaniesTable :data="companies" />
    </div>
  </div>
</template>
