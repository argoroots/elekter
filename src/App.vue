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
const selectedLowest = ref(new URLSearchParams(window.location.search).get('lowest') || null)
const prices = ref()
const options = ref({
  bar: { groupWidth: '75%' },
  chartArea: {
    left: 30,
    top: 5,
    width: '100%',
    height: '88%'
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

const data = computed(() => {
  if (!prices.value) return
  const { startIndex, endIndex } = selectedLowest.value ? lowest.value.find(x => x.value === selectedLowest.value) : {}

  if (startIndex >= 0 && endIndex >= 0) {
    return [
      [
        'Tund',
        'Elektriaktsiis',
        { role: 'style' },
        'Taastuvenergia tasu',
        { role: 'style' },
        'Elektri edastamine',
        { role: 'style' },
        'Elektri hind',
        { role: 'style' }
      ],
      ...prices.value.map((x, idx) => [
        x.at(0),
        x.at(1),
        idx >= startIndex && idx <= endIndex ? '#10b981' : null,
        x.at(2),
        idx >= startIndex && idx <= endIndex ? '#34d399' : null,
        x.at(3),
        idx >= startIndex && idx <= endIndex ? '#6ee7b7' : null,
        x.at(4),
        idx >= startIndex && idx <= endIndex ? '#a7f3d0' : null
      ])]
  } else {
    return [
      [
        'Tund',
        'Elektriaktsiis',
        'Taastuvenergia tasu',
        'Elektri edastamine',
        'Elektri hind'
      ],
      ...prices.value
    ]
  }
})

const lowest = computed(() => prices.value && [
  { value: '1h', ...findLowestTimeSpan(prices.value, 1) },
  { value: '2h', ...findLowestTimeSpan(prices.value, 2) },
  { value: '3h', ...findLowestTimeSpan(prices.value, 3) },
  { value: '4h', ...findLowestTimeSpan(prices.value, 4) }
])

watch(() => selectedPlan.value, (val) => {
  getPrices()

  const params = new URLSearchParams({
    plan: val.value,
    lowest: selectedLowest.value || ''
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => selectedLowest.value, (val) => {
  console.log(val)
  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    lowest: val || ''
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

onMounted(() => {
  getPrices()
  setInterval(() => { getPrices() }, 15 * 60 * 1000)
})

async function getPrices () {
  const response = await fetch('https://faas-fra1-afec6ce7.doserverless.co/api/v1/web/fn-97f69b9b-30c7-41dd-947b-f687dbc54ade/default/borsihind?plan=' + selectedPlan.value.value)
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

  return {
    start: prices[lowestSumIndex].at(0),
    startIndex: lowestSumIndex,
    end: prices[lowestSumIndex + span]?.at(0) || '01',
    endIndex: lowestSumIndex + span - 1,
    price: lowestSum / span
  }
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

  <main class="flex flex-col gap-8 md:gap-20">
    <GChart
      v-if="data"
      class="h-60 md:h-96"
      type="ColumnChart"
      :data="data"
      :options="options"
      :resize-debounce="500"
    />

    <div
      v-if="lowest"
      class="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-20 justify-between"
    >
      <div
        v-for="x in lowest"
        :key="x.index"
        class="p-4 flex flex-col gap-2 items-center cursor-pointer border  hover:border-green-300 rounded-lg"
        :class="selectedLowest === x.value ? 'border-green-300 bg-green-50' : 'border-transparent'"
        @click="selectedLowest = selectedLowest !== x.value ? x.value : null"
      >
        <div class="font-bold text-blue-400">
          {{ x.value }}
        </div>

        {{ x.start }}.00 – {{ x.end }}.00

        <div
          class="mt-1 py-1 px-2 text-xs text-green-600 border rounded"
          :class="selectedLowest === x.value ? 'font-bold border-transparent bg-transparent' : 'border-green-300 bg-green-50'"
        >
          {{ x.price.toFixed(2) }}
        </div>
      </div>
    </div>

    <div class="flex items-center justify-center">
      <Listbox v-model="selectedPlan">
        <div class="relative w-full sm:w-auto">
          <ListboxButton
            class="relative w-full cursor-default rounded-lg border bg-white py-2 pl-3 pr-10 text-left focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-blue-300 sm:text-sm"
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
              class="absolute bottom-11 max-h-60 w-full overflow-auto rounded-md bg-white py-1 ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm"
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

    <div class="pb-2 italic text-sm text-center">
      Hinnad on koos käibemaksuga, sentides kilovatt-tunni kohta.
    </div>
  </main>
</template>
