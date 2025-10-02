import { h, render } from 'vue'

export function useChartTooltip () {
  function createTooltip (startTime, priceData, marginalValue, colors, isHourly) {
    const [hours, minutes] = startTime.split(':').map(Number)
    const intervalMinutes = isHourly ? 60 : 15
    const endMinutes = minutes + intervalMinutes
    const endHours = hours + Math.floor(endMinutes / 60)
    const endMins = endMinutes % 60
    const endTime = `${String(endHours % 24).padStart(2, '0')}:${String(endMins).padStart(2, '0')}`
    const total = marginalValue + priceData[0] + priceData[1] + priceData[2] + priceData[3]

    const rows = [
      { label: 'Elektri hind:', value: priceData[3].toFixed(2), color: colors[4] },
      { label: 'Elektri edastamine:', value: priceData[2].toFixed(2), color: colors[3] },
      { label: 'Taastuvenergia tasu:', value: priceData[1].toFixed(2), color: colors[2] },
      { label: 'Elektriaktsiis:', value: priceData[0].toFixed(2), color: colors[1] },
      { label: 'Müüa marginaal:', value: marginalValue.toFixed(3), color: colors[0] }
    ]

    const vnode = h('div', { class: 'p-2 font-sans whitespace-nowrap' }, [
      h('div', { class: 'font-bold mb-2 text-center' }, `${startTime} - ${endTime}`),
      ...rows.map((row, index) =>
        h('div', { class: 'flex items-center justify-between mb-1' }, [
          h('span', { class: 'flex items-center' }, [
            h('span', { class: 'inline-block w-3 h-3 mr-1.5', style: { backgroundColor: row.color } }),
            row.label
          ]),
          h('span', { class: 'ml-3' }, row.value)
        ])
      ),
      h('div', { class: 'text-center font-bold mt-2' }, total.toFixed(2))
    ])

    const container = document.createElement('div')
    render(vnode, container)

    return container.innerHTML
  }

  return {
    createTooltip
  }
}
