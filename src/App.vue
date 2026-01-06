<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { GChart } from 'vue-google-charts'
import { useChartTooltip } from './composables/useChartTooltip.js'
import AppSelect from './components/AppSelect.vue'

const { createTooltip } = useChartTooltip()

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
const blueColors = ['#1e40af', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe']
const greenColors = ['#065f46', '#047857', '#059669', '#10b981', '#34d399', '#6ee7b7']

// Refs
const selectedPlan = ref(plans.find(x => x.value === (new URLSearchParams(window.location.search).get('plan') || 'V1')))
const selectedInterval = ref(intervals.find(x => x.value === (new URLSearchParams(window.location.search).get('interval') || '15min')))
const selectedLowest = ref(new URLSearchParams(window.location.search).get('lowest') || null)
const marginal = ref(parseFloat(new URLSearchParams(window.location.search).get('marginal') || '0'))
const prices = ref()
const rawPrices = ref()

// Computed
const is1h = computed(() => selectedInterval.value.value === '1h')

const options = computed(() => ({
  bar: { groupWidth: '75%' },
  chartArea: {
    left: 30,
    top: 5,
    bottom: 60,
    width: '100%',
    height: '75%'
  },
  focusTarget: 'category',
  fontName: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
  fontSize: 13,
  isStacked: true,
  legend: { position: 'none' },
  tooltip: { isHtml: true },
  hAxis: {
    slantedText: false,
    slantedTextAngle: 0
  }
}))

const data = computed(() => {
  if (!prices.value) return

  const { startIndex, endIndex } = selectedLowest.value ? lowest.value.find(x => x.value === selectedLowest.value) : {}
  const marginalValue = marginal.value || 0
  const hasSelection = startIndex >= 0 && endIndex >= 0

  const header = [
    'Aeg',
    { type: 'string', role: 'tooltip', p: { html: true } },
    'Müüja marginaal',
    { role: 'style' },
    'Elektriaktsiis',
    { role: 'style' },
    'Varustuskindluse tasu',
    { role: 'style' },
    'Taastuvenergia tasu',
    { role: 'style' },
    'Elektri edastamine',
    { role: 'style' },
    'Elektri hind',
    { role: 'style' }
  ]

  const rows = prices.value.map((x, idx) => {
    const time = Array.isArray(x) ? x[0] : x.at(0)
    const priceData = Array.isArray(x) ? [x[1], x[2], x[3], x[4], x[5]] : [x.at(1), x.at(2), x.at(3), x.at(4), x.at(5)]
    const year = Array.isArray(x) ? x[6] : x.at(6)
    const month = Array.isArray(x) ? x[7] : x.at(7)
    const isSelected = hasSelection && idx >= startIndex && idx <= endIndex
    const colors = isSelected ? greenColors : blueColors

    return [
      formatLabelForChart(time),
      createTooltip(time, priceData, marginalValue, colors, is1h.value),
      marginalValue,
      colors[0],
      priceData[0],
      colors[1],
      priceData[1],
      colors[2],
      priceData[2],
      colors[3],
      priceData[3],
      colors[4],
      priceData[4],
      colors[5]
    ]
  })

  return [header, ...rows]
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
    lowest: selectedLowest.value || '',
    marginal: marginal.value.toString()
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => selectedInterval.value, (val) => {
  updatePrices()

  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    interval: val.value,
    lowest: selectedLowest.value || '',
    marginal: marginal.value.toString()
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => selectedLowest.value, (val) => {
  console.log(val)
  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    interval: selectedInterval.value.value,
    lowest: val || '',
    marginal: marginal.value.toString()
  })
  window.history.replaceState({}, '', `?${params.toString()}`)
})

watch(() => marginal.value, (val) => {
  const params = new URLSearchParams({
    plan: selectedPlan.value.value,
    interval: selectedInterval.value.value,
    lowest: selectedLowest.value || '',
    marginal: val.toString()
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
        const avgSupplyFee = hourlyValues.reduce((sum, v) => sum + v[5], 0) / hourlyValues.length
        const firstValue = hourlyValues[0]

        hourlyData.push([
          `${currentHour}:00`,
          avgExcise,
          avgRenewable,
          avgTransmission,
          avgPrice,
          avgSupplyFee,
          firstValue[6], // year
          firstValue[7], // month
          firstValue[8] // day
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
    const avgSupplyFee = hourlyValues.reduce((sum, v) => sum + v[5], 0) / hourlyValues.length
    const firstValue = hourlyValues[0]

    hourlyData.push([
      `${currentHour}:00`,
      avgExcise,
      avgRenewable,
      avgTransmission,
      avgPrice,
      avgSupplyFee,
      firstValue[6], // year
      firstValue[7], // month
      firstValue[8] // day
    ])
  }

  return hourlyData
}

async function getPrices () {
  const response = await fetch(`https://argoroots-public.s3.eu-central-1.amazonaws.com/borsihind/${selectedPlan.value.value}.json`)
  const responseJson = await response.json()

  rawPrices.value = responseJson.map((x) => [
    x.at(3).toString().padStart(2, '0') + ':' + x.at(4).toString().padStart(2, '0'),
    x.at(8) * 100, // excise
    x.at(9) * 100, // supply security fee
    x.at(7) * 100, // renewable tax
    x.at(6) * 100, // grid transmission
    x.at(5) * 100, // electricity price
    x.at(0), // year
    x.at(1), // month
    x.at(2) // day
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

  const pricesSum = prices.map((x) => x.at(1) + x.at(2) + x.at(3) + x.at(4) + x.at(5))

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
        <div
          class="font-bold"
          :class="{ 'text-green-600': selectedLowest === x.value, 'text-blue-400': selectedLowest !== x.value }"
        >
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
      <AppSelect
        v-model="selectedInterval"
        :options="intervals"
        label="Intervall: "
      />

      <AppSelect
        v-model="selectedPlan"
        :options="plans"
        label="Elektrilevi võrguteenus: "
      />

      <div class="relative w-full sm:w-auto">
        <div class="flex items-center rounded-lg border bg-white h-[38px] px-3 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-white focus-within:ring-opacity-75 focus-within:ring-offset-2 focus-within:ring-offset-blue-300 sm:text-sm">
          <label class="mr-2">Marginaal:</label>
          <input
            v-model.number="marginal"
            type="number"
            step="0.01"
            class="w-20 focus:outline-none bg-transparent"
          >
        </div>
      </div>
    </div>

    <div class="pb-2 italic text-sm text-center">
      Hinnad on koos käibemaksuga, sentides kilovatt-tunni kohta.
    </div>
  </main>
</template>
