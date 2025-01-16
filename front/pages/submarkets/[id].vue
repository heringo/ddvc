<script lang="ts" setup>
import { cn } from "@/lib/utils";

import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

import CompaniesTable from "@/components/CompaniesTable.vue";
import { BarChart } from "@/components/ui/chart-bar";
import { AreaChart } from "@/components/ui/chart-area";
import { CurveType } from "@unovis/ts";

const router = useRouter();
const supabase: any = useSupabaseClient();

const submarket = ref();
const companies = ref();
const news = ref();

const { id } = useRoute().params;

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

const {
  data: timeseriesData,
  error: timeseriesError,
}: { data: any; error: any } = await useAsyncData(() =>
  supabase
    .from("harmonic_data")
    .select("*")
    .in(
      "company_id",
      companiesData?.value?.data?.map((company: any) => company.id)
    )
    .eq("type", "similarweb_visits")
);

console.log("timeseriesData", timeseriesData);

let webTrafficPerMonth = timeseriesData.value.data.reduce(
  (acc: any, item: any) => {
    const date = item.date.split("T")[0]; // Extract date in 'yyyy-mm-dd' format
    if (!acc[date]) {
      acc[date] = 0; // Initialize the date entry if not exists
    }
    acc[date] += item.value; // Accumulate the values for the same date
    return acc;
  },
  {}
);

webTrafficPerMonth = Object.entries(webTrafficPerMonth).map(
  ([date, value]) => ({
    date,
    value,
  })
);

const openPage = (url: string) => {
  window.open(url, "_blank");
};

submarket.value = submarketData?.value?.data;
companies.value = companiesData?.value?.data?.sort(
  (a: any, b: any) => b.funding_amount - a.funding_amount
);
news.value = newsData?.value?.data;

let companiesPerStage = companies.value.reduce((acc: any, company: any) => {
  if (!acc[company.funding_stage]) {
    acc[company.funding_stage] = 0;
  }

  if (!acc[company.funding_stage]) {
    acc[company.funding_stage] = 0;
  }

  acc[company.funding_stage] += 1;

  return acc;
}, {});

let companiesPerCountry = companies.value.reduce((acc: any, company: any) => {
  if (!company.country) {
    return acc;
  }

  if (!acc[company.country]) {
    acc[company.country] = 0;
  }

  acc[company.country] += 1;

  return acc;
}, {});

let companiesFoundedPerYear = companies.value.reduce(
  (acc: any, company: any) => {
    if (!company?.founded_at) {
      return acc;
    }

    const foundedAt = new Date(company.founded_at);
    const foundingYear = foundedAt.getFullYear();

    if (!acc[foundingYear]) {
      acc[foundingYear] = 0;
    }

    acc[foundingYear] += 1;

    return acc;
  },
  {}
);

// transform companiesPerStage to array of objects containing {stage: string, count: number}
companiesPerStage = Object.entries(companiesPerStage)
  .map(([stage, count]) => {
    return {
      stage: formatFunding(stage),
      count,
    };
  })
  .filter((c: any) => c.stage && c.stage !== "null");

// transform companiesPerCountry to array of objects containing {country: string, count: number}
companiesPerCountry = Object.entries(companiesPerCountry)
  .map(([country, count]) => {
    return {
      country,
      count,
    };
  })
  .filter((c: any) => c.country && c.country !== "null");

companiesFoundedPerYear = Object.entries(companiesFoundedPerYear)
  .map(([year, count]) => {
    return {
      year,
      count,
    };
  })
  .filter((c: any) => c.year && c.year !== "null");
</script>

<template>
  <div class="container min-h-screen flex flex-row py-12 justify-center">
    <div class="text-justify w-full sm:w-2/3 xl:w-2/3">
      <NuxtLink to="/" class="flex flex-row items-center mb-2">
        <Logo class="w-4 h-4 mr-1" />
        <h1 class="text-xl font-bold">Pulse</h1>
      </NuxtLink>
      <h1 class="text-4xl text-left font-bold mb-1">
        {{ submarket?.topic_name }}
      </h1>
      <p class="text-gray-500 mb-2">
        {{ submarket?.topic_description }}
      </p>

      <h3 class="text-2xl font-bold mb-4">Company distribution</h3>

      <div class="flex md:flex-row space-x-4">
        <div class="w-1/2 black-shadow p-4">
          <h4 class="text-lg mb-1">Company count per deal stage</h4>
          <BarChart
            index="stage"
            :data="companiesPerStage"
            :categories="['count']"
            :class="' h-64'"
            :y-formatter="
              (tick, i) => {
                return typeof tick === 'number'
                  ? `${new Intl.NumberFormat('us').format(tick).toString()}`
                  : '';
              }
            "
            :type="'grouped'"
            :showGridLine="true"
            :showLegend="false"
          />
        </div>
        <div class="w-1/2 black-shadow p-4">
          <h4 class="text-lg mb-1">Company count per country</h4>
          <BarChart
            index="country"
            :data="companiesPerCountry"
            :categories="['count']"
            :y-formatter="
              (tick, i) => {
                return typeof tick === 'number'
                  ? `${new Intl.NumberFormat('us').format(tick).toString()}`
                  : '';
              }
            "
            :type="'grouped'"
            :class="' h-64'"
            :showGridLine="true"
            :showLegend="false"
          />
        </div>
      </div>

      <div class="p-4 black-shadow mt-4 h-96">
        <h4 class="text-lg mb-8">Companies founded over time</h4>

        <AreaChart
          :class="'h-64'"
          index="year"
          :data="companiesFoundedPerYear"
          :categories="['count']"
          :show-grid-line="true"
          :show-legend="false"
          :y-formatter="
            (tick, i) => {
              return typeof tick === 'number'
                ? `${new Intl.NumberFormat('us').format(tick).toString()}`
                : '';
            }
          "
          :show-x-axis="true"
          :show-y-axis="true"
          :curve-type="CurveType.Linear"
        />
      </div>

      <h3 class="text-2xl font-bold mb-4 mt-4">Web traffic trends</h3>
      <div class="p-4 black-shadow mt-4 h-96">
        <h4 class="text-lg mb-8">Sum of traffic across companies</h4>

        <AreaChart
          :class="'h-64'"
          index="date"
          :data="webTrafficPerMonth"
          :categories="['value']"
          :show-grid-line="true"
          :show-legend="false"
          :y-formatter="
            (tick, i) => {
              return typeof tick === 'number'
                ? `${new Intl.NumberFormat('us').format(tick).toString()}`
                : '';
            }
          "
          :show-x-axis="true"
          :show-y-axis="true"
          :curve-type="CurveType.Linear"
        />
      </div>

      <h3 class="text-2xl font-bold mb-0 mt-4">Latest news</h3>

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
                n.effective_date
                  ? new Date(n.effective_date).toLocaleDateString("en-US", {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    }) + " - "
                  : ""
              }}
              {{ n.article_title }}
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
