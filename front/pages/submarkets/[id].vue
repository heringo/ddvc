<script lang="ts" setup>
import { cn } from "@/lib/utils";

import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

import CompaniesTable from "@/components/CompaniesTable.vue";

const router = useRouter();
const supabase: any = useSupabaseClient();

const submarket = ref();
const companies = ref();
const news = ref();

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

const { data: newsData, error: newsError }: { data: any; error: any } =
  await useAsyncData(() =>
    supabase
      .from("predict_leads_news")
      .select("*")
      .in(
        "company_id",
        companiesData?.value?.data?.map((company: any) => company.id)
      )
  );

const openPage = (url: string) => {
  window.open(url, "_blank");
};

submarket.value = submarketData?.value?.data;
companies.value = companiesData?.value?.data?.sort(
  (a: any, b: any) => b.funding_amount - a.funding_amount
);
news.value = newsData?.value?.data;

console.log(news.value);
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

      <h3 class="text-2xl font-bold mb-0">Latest news</h3>

      <div class="flex flex-col">
        <div
          v-for="n in news.slice(0, 5).sort((a: any, b: any) => new Date((b).effective_date) - new Date(a.effective_date))"
          :key="n.id"
          :class="cn('p-4 black-shadow with-hover mt-3 cursor-pointer')"
          @click="openPage(n.article_url)"
        >
          <div class="flex flex-row items-center mb-1">
            <img
              :src="companies.find((c: any) => c.id === n.company_id)?.logo_url"
              class="w-6 h-6 mr-2 border rounded-full"
            />
            <h4 class="text-sm font-bold text-left flex-1">
              {{
                new Date(n.effective_date).toLocaleDateString("en-US", {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
                })
              }}
              - {{ n.article_title }}
            </h4>
          </div>
          <p class="text-gray-500 text-xs">
            {{ n.article_body.substring(0, 200) }}
            {{ n.article_body.length > 200 ? "..." : "" }}
          </p>
        </div>
      </div>

      <h3 class="text-2xl font-bold mb-4 mt-8">Companies</h3>
      <CompaniesTable :data="companies" />
    </div>
  </div>
</template>
