<script setup lang="ts">
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Icon } from "@iconify/vue";
import Logo from "@/components/Logo.vue";

const search = ref("");
const searched = ref(false);
const submarkets = ref();

const router = useRouter();
const supabase = useSupabaseClient();

// Sorts an array of fundings ["SERIES_E", "PRE-SEED", "SERIES_A", "SEED", "EXITED", "STEALTH"]
// by first removing null, "EXITED", "STEALTH", "VENTURE_UNKNOWN"
// then sorting by ["PRE-SEED", "SEED", "SERIES_A", "SERIES_B", "SERIES_C", "SERIES_D", "SERIES_E"]
const sortFundings = (fundings: any) => {
  const order = [
    "PRE_SEED",
    "SEED",
    "SERIES_A",
    "SERIES_B",
    "SERIES_C",
    "SERIES_D",
    "SERIES_E",
  ];

  return fundings
    .filter(
      (funding: any) =>
        funding &&
        funding !== "EXITED" &&
        funding !== "STEALTH" &&
        funding !== "VENTURE_UNKNOWN"
    )
    .sort((a: any, b: any) => order.indexOf(a) - order.indexOf(b));
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

const getSubmarkets = async () => {
  let { data, error }: { data: any; error: any } = await supabase
    .from("submarkets")
    .select("*");

  let { data: submarkets_companies, error: error2 }: { data: any; error: any } =
    await supabase.from("submarkets_companies").select("*");

  data = data?.map((submarket: any) => {
    return {
      ...submarket,
      sortedFundings: sortFundings(submarket.funding_stages),
      companies: submarkets_companies.filter(
        (company: any) => company.topic_id === submarket.id
      ),
    };
  });

  console.log(data);

  // remove outliers topic
  submarkets.value = data.filter((submarket: any) => submarket.id != 14);
  console.log(error);

  searched.value = true;
};
</script>

<template>
  <div>
    <div
      class="container min-h-screen flex flex-row py-12 justify-center items-center"
      v-if="!searched"
    >
      <div class="text-center">
        <div class="flex flex-row items-center text-center justify-center">
          <Logo class="w-8 h-8 mr-1" />
          <h1 class="text-4xl font-bold">Pulse</h1>
        </div>
        <p class="text-gray-500 mb-4">Get the pulse of any market</p>

        <div class="flex flex-row justify-center items-center">
          <Input
            v-model="search"
            placeholder="Query a topic you want to discover (e.g: Open-source, ...)"
            class="w-96 black-shadow"
          />

          <Button @click="getSubmarkets" class="ml-2 black-shadow with-hover">
            <Icon
              icon="lucide:search"
              class="mr-2"
              style="color: black !important"
            />
            Search
          </Button>
        </div>
      </div>
    </div>

    <div class="container min-h-screen flex flex-col py-12" v-if="searched">
      <NuxtLink
        to="/"
        class="flex flex-row items-center justify-center"
        @click="searched = false"
      >
        <Logo class="w-6 h-6 mr-1" />
        <h1 class="text-2xl font-bold">Pulse</h1>
      </NuxtLink>
      <h2 class="text-4xl font-bold text-center">Open-source</h2>
      <p class="text-gray-500 text-center">
        Explore all submarkets related to open-source
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-12 mt-8">
        <div
          v-for="submarket in submarkets"
          :key="submarket.id"
          class="p-4 flex flex-col black-shadow with-hover cursor-pointer"
          @click="router.push(`/submarkets/${submarket.id}`)"
        >
          <h3 class="text-xl font-bold">
            {{ submarket.topic_name }}
          </h3>
          <div class="flex flex-row w-full">
            <div class="relative h-8 w-8 my-1">
              <img
                v-for="(company, index) in submarket.companies"
                :key="company.id"
                :src="company.logo_url"
                class="absolute h-8 w-8 rounded-full border bg-white"
                :style="{
                  left: `${(submarket.companies.length - index - 1) * 20}px`,
                  zIndex: 100 - index,
                }"
              />
              <span
                v-if="submarket.companies.length > 1"
                class="absolute text-sm"
                :style="{
                  left: `${submarket.companies.length * 20 + 20}px`,
                  zIndex: 101,
                  width: '80px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                }"
              >
                +{{ submarket.company_count - submarket.companies.length }} more
              </span>
            </div>
          </div>
          <p class="text-gray-500 mb-4 mt-1">
            {{ submarket?.topic_description }}
          </p>

          <div class="flex flex-col flex-1 justify-end">
            <div class="flex flex-row justify-between">
              <span
                class="px-2 py-1 rounded-xl bg-gray-100 border border-gray-300 text-sm"
                >Most advanced:
                {{
                  formatFunding(
                    submarket.sortedFundings[
                      submarket.sortedFundings.length - 1
                    ]
                  )
                }}</span
              >
              <span
                class="px-2 py-1 rounded-xl bg-gray-100 border border-gray-300 text-sm"
                >First mover:
                {{
                  new Date(submarket.earliest_founded_at).getFullYear()
                }}</span
              >
            </div>
            <div class="flex flex-row justify-between mt-2">
              <span
                class="px-2 py-1 rounded-xl bg-gray-100 border border-gray-300 text-sm"
                >Total funding ${{
                  formatAmount(submarket.total_funding)
                }}</span
              >
              <span
                class="px-2 py-1 rounded-xl bg-gray-100 border border-gray-300 text-sm"
                >Main geography:
                {{
                  submarket.most_common_geography == "USA"
                    ? "🇺🇸"
                    : submarket.most_common_geography == "Europe"
                    ? "🇪🇺"
                    : "🌎"
                }}
                {{ submarket.most_common_geography }}
              </span>
              <!-- company per stage -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.black-shadow,
#companies-table .black-shadow {
  border-radius: 0 !important;
  background-color: white;
  color: black;
  box-shadow: 3px 3px 0px 0px black;
  border: solid 1px black !important;
  transition: all 0.2s ease-in-out !important;
  position: relative;
}

.black-shadow.with-hover:hover,
#companies-table .black-shadow.with-hover:hover {
  transform: translate(2.5px, 2.5px);
  box-shadow: 0.5px 0.5px 0.5px 0.5px black;
  background-color: white;
  color: black;
}
</style>
