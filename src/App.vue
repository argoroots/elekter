<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { GChart } from 'vue-google-charts'
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'

const plans = [
  { value: 'V1', label: 'Võrk 1' },
  { value: 'V2', label: 'Võrk 2' },
  { value: 'V2k', label: 'Võrk 2 kuutasuga' },
  { value: 'V4', label: 'Võrk 4' },
  { value: 'V5', label: 'Võrk 5' }
]
const selectedPlan = ref(plans.find(x => x.value === (new URLSearchParams(window.location.search).get('plan') || 'V1')))
const prices = ref()
const options = ref({
  bar: { groupWidth: '75%' },
  chartArea: {
    left: 30,
    top: 5,
    width: '100%',
    height: '90%'
  },
  focusTarget: 'category',
  fontName: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
  fontSize: 13,
  isStacked: true,
  legend: { position: 'none' },
  series: {
    0: { color: '#3b82f6' },
    1: { color: '#60a5fa' },
    2: { color: '#93c5fd' },
    3: { color: '#bfdbfe' }
  }
})

const data = computed(() => prices.value && [
  [
    'Tund',
    'Elektriaktsiis',
    'Taastuvenergia tasu',
    'Elektri edastamine',
    'Elektri hind'
  ],
  ...prices.value
])

const lowest = computed(() => prices.value && [
  ['1h', ...findLowestTimeSpan(prices.value, 1)],
  ['2h', ...findLowestTimeSpan(prices.value, 2)],
  ['3h', ...findLowestTimeSpan(prices.value, 3)],
  ['4h', ...findLowestTimeSpan(prices.value, 4)]
])

watch(() => selectedPlan.value, (val) => {
  window.history.replaceState({}, '', '?plan=' + val.value)
  getPrices()
})

onMounted(getPrices)

async function getPrices () {
  const response = await fetch('https://api.roots.ee/elekter?plan=' + selectedPlan.value.value)
  const responseJson = await response.json()

  prices.value = responseJson.map((x) => [
    x.at(3).toString().padStart(2, '0'),
    x.at(7) * 100,
    x.at(6) * 100,
    x.at(5) * 100,
    x.at(4) * 100
  ])
}

function findLowestTimeSpan (prices, span) {
  if (prices.length === 0) return []

  const pricesSum = prices.map((x) => x.at(1) + x.at(2) + x.at(3) + x.at(4))

  let lowestSum = Infinity
  let lowestSumIndex = -1

  for (let i = 0; i < pricesSum.length - span + 1; i++) {
    const sum = pricesSum.slice(i, i + span).reduce((acc, val) => acc + val, 0)

    if (sum < lowestSum) {
      lowestSum = sum
      lowestSumIndex = i
    }
  }

  return [prices[lowestSumIndex].at(0), prices[lowestSumIndex + span].at(0), lowestSum / span]
}
</script>

<template>
  <header class="w-full">
    <h1 class="mx-auto w-max text-2xl text-center font-bold text-stone-900/80 tracking-wide">
      Elektri börsihind
      <span class="block italic text-right text-sm font-thin">by <a
        class="hover:underline"
        href="mailto:argo@roots.ee?subject=Elektri börsihind"
      >Argo Roots</a></span>
    </h1>
  </header>

  <main class="flex flex-col gap-20">
    <GChart
      class="h-96"
      type="ColumnChart"
      :data="data"
      :options="options"
      :resize-debounce="500"
    />

    <div
      v-if="lowest"
      class="grid grid-cols-1 sm:grid-cols-4 gap-20 justify-between"
    >
      <div
        v-for="x in lowest"
        :key="x.at(0)"
        class="flex flex-col gap-2 items-center"
      >
        <div class="font-bold text-blue-400">
          {{ x.at(0) }}
        </div>

        {{ x.at(1) }}.00 – {{ x.at(2) }}.00

        <div class="mt-1 py-1 px-2 text-xs text-green-600 border border-green-300 bg-green-50 rounded">
          {{ x.at(3).toFixed(2) }}
        </div>
      </div>
    </div>

    <div class="flex items-center justify-center">
      <Listbox v-model="selectedPlan">
        <div class="relative">
          <ListboxButton
            class="relative w-full cursor-default rounded-lg border bg-white py-2 pl-3 pr-10 text-left focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm"
          >
            <span class="block truncate">Elektrilevi võrguteenus: {{ selectedPlan.label }}</span>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon
                class="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </ListboxButton>

          <transition
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
          >
            <ListboxOptions
              class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
            >
              <ListboxOption
                v-for="plan in plans"
                v-slot="{ active, selected }"
                :key="plan.label"
                :value="plan"
                as="template"
              >
                <li
                  :class="[
                    active ? 'bg-blue-100 text-blue-900' : '',
                    'relative cursor-default select-none py-2 pl-10 pr-4',
                  ]"
                >
                  <span
                    :class="[
                      selected ? 'font-medium' : 'font-normal',
                      'block truncate',
                    ]"
                  >{{ plan.label }}</span>
                  <span
                    v-if="selected"
                    class="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600"
                  >
                    <CheckIcon
                      class="h-5 w-5"
                      aria-hidden="true"
                    />
                  </span>
                </li>
              </ListboxOption>
            </ListboxOptions>
          </transition>
        </div>
      </Listbox>
    </div>

    <div class="italic text-sm text-center">
      Hinnad on koos käibemaksuga, sentides kilovatt-tunni kohta.
    </div>
  </main>
</template>
