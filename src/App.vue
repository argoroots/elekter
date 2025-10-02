<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { GChart } from 'vue-google-charts'
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'

// Constants
const plans = [
  { value: 'V1', label: 'Võrk 1' },
  { value: 'V2', label: 'Võrk 2' },
  { value: 'V4', label: 'Võrk 4' },
  { value: 'V5', label: 'Võrk 5' }
]
const intervals = [
  { value: '15min', label: '15 minutit' },
  { value: '1h', label: '1 tund' }
]

// Refs
const selectedPlan = ref(plans.find(x => x.value === (new URLSearchParams(window.location.search).get('plan') || 'V1')))
const selectedInterval = ref(intervals.find(x => x.value === (new URLSearchParams(window.location.search).get('interval') || '15min')))
const selectedLowest = ref(new URLSearchParams(window.location.search).get('lowest') || null)
const prices = ref()
const rawPrices = ref()

// Computed
const is1h = computed(() => selectedInterval.value.value === '1h')

const options = computed(() => ({
  bar: { groupWidth: '75%' },
  chartArea: {
    left: 30,
    top: 5,
    width: '100%',
    height: '80%'
  },
  focusTarget: 'category',
  fontName: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
  fontSize: 13,
  isStacked: true,
  legend: { position: 'none' },
  hAxis: {
    slantedText: false,
    slantedTextAngle: 0
  },
  series: {
    0: { color: '#3b82f6' },
    1: { color: '#60a5fa' },
    2: { color: '#93c5fd' },
    3: { color: '#bfdbfe' }
  }
}))

const data = computed(() => {
  if (!prices.value) return
  const { startIndex, endIndex } = selectedLowest.value ? lowest.value.find(x => x.value === selectedLowest.value) : {}

  if (startIndex >= 0 && endIndex >= 0) {
    return [
      [
        'Aeg',
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
        formatLabelForChart(x.at(0)),
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
        'Aeg',
        'Elektriaktsiis',
        'Taastuvenergia tasu',
        'Elektri edastamine',
        'Elektri hind'
      ],
      ...prices.value.map(x => [formatLabelForChart(x[0]), x[1], x[2], x[3], x[4]])
    ]
  }
})

const lowest = computed(() => {
  if (!prices.value) return null

  const multiplier = is1h.value ? 1 : 4

  return [
    { value: '1h', ...findLowestTimeSpan(prices.value, 1 * multiplier) },
    { value: '2h', ...findLowestTimeSpan(prices.value, 2 * multiplier) },
    { value: '3h', ...findLowestTimeSpan(prices.value, 3 * multiplier) },
    { value: '4h', ...findLowestTimeSpan(prices.value, 4 * multiplier) }
  ]
})

// Watchers
watch(() => selectedPlan.value, (val) => {
  getPrices()

  const params = new URLSearchParams({
    plan: val.value,
    interval: selectedInterval.value.value,
    lowest: selectedLowest.value || ''
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => selectedInterval.value, (val) => {
  updatePrices()

  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    interval: val.value,
    lowest: selectedLowest.value || ''
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => selectedLowest.value, (val) => {
  console.log(val)
  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    interval: selectedInterval.value.value,
    lowest: val || ''
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

// Lifecycle
onMounted(() => {
  getPrices()
  setInterval(() => { getPrices() }, 15 * 60 * 1000)
})

// Functions
function formatLabelForChart (label) {
  // For 15min interval, only show labels on full hours and remove :00
  if (!is1h.value) {
    if (!label.endsWith(':00')) {
      return ''
    }
    return label.slice(0, -3)
  }

  // For 1h interval, remove :00
  if (label.endsWith(':00')) {
    return label.slice(0, -3)
  }

  return label
}

function aggregateToHourly (pricesData) {
  if (!pricesData || pricesData.length === 0) return []

  const hourlyData = []
  let currentHour = null
  let hourlyValues = []

  pricesData.forEach((price) => {
    const hour = price[0].split(':')[0]

    if (currentHour === null) {
      currentHour = hour
    }

    if (hour !== currentHour) {
      // Calculate averages for the completed hour
      if (hourlyValues.length > 0) {
        const avgExcise = hourlyValues.reduce((sum, v) => sum + v[1], 0) / hourlyValues.length
        const avgRenewable = hourlyValues.reduce((sum, v) => sum + v[2], 0) / hourlyValues.length
        const avgTransmission = hourlyValues.reduce((sum, v) => sum + v[3], 0) / hourlyValues.length
        const avgPrice = hourlyValues.reduce((sum, v) => sum + v[4], 0) / hourlyValues.length

        hourlyData.push([
          `${currentHour}:00`,
          avgExcise,
          avgRenewable,
          avgTransmission,
          avgPrice
        ])
      }

      currentHour = hour
      hourlyValues = []
    }

    hourlyValues.push(price)
  })

  // Don't forget the last hour
  if (hourlyValues.length > 0) {
    const avgExcise = hourlyValues.reduce((sum, v) => sum + v[1], 0) / hourlyValues.length
    const avgRenewable = hourlyValues.reduce((sum, v) => sum + v[2], 0) / hourlyValues.length
    const avgTransmission = hourlyValues.reduce((sum, v) => sum + v[3], 0) / hourlyValues.length
    const avgPrice = hourlyValues.reduce((sum, v) => sum + v[4], 0) / hourlyValues.length

    hourlyData.push([
      `${currentHour}:00`,
      avgExcise,
      avgRenewable,
      avgTransmission,
      avgPrice
    ])
  }

  return hourlyData
}

async function getPrices () {
  const response = await fetch(`https://argoroots-public.s3.eu-central-1.amazonaws.com/borsihind/${selectedPlan.value.value}.json`)
  const responseJson = await response.json()

  rawPrices.value = responseJson.map((x) => [
    x.at(3).toString().padStart(2, '0') + ':' + x.at(4).toString().padStart(2, '0'),
    x.at(8) * 100,
    x.at(7) * 100,
    x.at(6) * 100,
    x.at(5) * 100
  ])

  updatePrices()
}

function updatePrices () {
  if (!rawPrices.value) return

  if (is1h.value) {
    prices.value = aggregateToHourly(rawPrices.value)
  } else {
    prices.value = rawPrices.value
  }
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

  // Calculate end time based on interval
  const minutesPerUnit = is1h.value ? 60 : 15

  const startTime = prices[lowestSumIndex].at(0)
  const [startHours, startMinutes] = startTime.split(':').map(Number)

  const totalMinutes = span * minutesPerUnit
  const endTime = new Date()
  endTime.setHours(startHours, startMinutes + totalMinutes, 0, 0)

  const endTimeStr = endTime.getHours().toString().padStart(2, '0') + ':' + endTime.getMinutes().toString().padStart(2, '0')

  return {
    start: prices[lowestSumIndex].at(0),
    startIndex: lowestSumIndex,
    end: endTimeStr,
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
        class="p-4 flex flex-col gap-2 items-center cursor-pointer border hover:border-green-300 rounded-lg"
        :class="{ 'border-green-300 bg-green-50': selectedLowest === x.value, 'border-transparent': selectedLowest !== x.value }"
        @click="selectedLowest = selectedLowest !== x.value ? x.value : null"
      >
        <div class="font-bold text-blue-400">
          {{ x.value }}
        </div>

        {{ x.start }} – {{ x.end }}

        <div
          class="mt-1 py-1 px-2 text-xs text-green-600 border rounded"
          :class="{ 'font-bold border-transparent bg-transparent': selectedLowest === x.value, 'border-green-300 bg-green-50': selectedLowest !== x.value }"
        >
          {{ x.price.toFixed(2) }}
        </div>
      </div>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 items-center justify-center">
      <Listbox v-model="selectedInterval">
        <div class="relative w-full sm:w-auto">
          <ListboxButton
            class="relative w-full cursor-default rounded-lg border bg-white py-2 pl-3 pr-10 text-left focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-blue-300 sm:text-sm"
          >
            <span class="block truncate">Intervall: {{ selectedInterval.label }}</span>
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
                v-for="interval in intervals"
                v-slot="{ active, selected }"
                :key="interval.value"
                :value="interval"
                as="template"
              >
                <li
                  class="relative cursor-default select-none py-2 pl-10 pr-4"
                  :class="{ 'bg-blue-100 text-blue-900': active }"
                >
                  <span
                    class="block truncate"
                    :class="{ 'font-medium': selected, 'font-normal': !selected }"
                  >{{ interval.label }}</span>
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
                  class="relative cursor-default select-none py-2 pl-10 pr-4"
                  :class="{ 'bg-blue-100 text-blue-900': active }"
                >
                  <span
                    class="block truncate"
                    :class="{ 'font-medium': selected, 'font-normal': !selected }"
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
