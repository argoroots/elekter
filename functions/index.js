const http = require('https')

function getPrices (start, end) {
  return new Promise((resolve, reject) => {
    const url = `https://dashboard.elering.ee/api/nps/price?start=${start.toISOString().substring(0, 13)}:00:00.000Z&end=${end.toISOString().substring(0, 13)}:00:00.000Z`

    http.get(url, (response) => {
      let body = ''

      response.on('data', function (d) {
        body += d
      })

      response.on('end', function () {
        try {
          resolve(JSON.parse(body).data.ee)
        } catch (e) {
          console.log(body)
          console.error(e)
          resolve([])
        }
      })
    })
  })
}

function changeTimeZone (date, timeZone) {
  if (typeof date === 'string') {
    return new Date(
      new Date(date).toLocaleString('en-US', {
        timeZone
      })
    )
  }

  return new Date(
    date.toLocaleString('en-US', {
      timeZone
    })
  )
}

function getGridFee (date, service = 'V4') {
  const plans = {
    V1: {
      price: 0.0865
    },
    V2: {
      day: 0.1042,
      night: 0.0606
    },
    V2k: {
      day: 0.0680,
      night: 0.0394
    },
    V4: {
      day: 0.0443,
      night: 0.0252

    },
    V5: {
      day: 0.0617,
      dayTop: 0.0953,
      night: 0.0354,
      nightTop: 0.0552
    }
  }
  const holidays = ['2023-01-01', '2023-02-24', '2023-04-07', '2023-04-09', '2023-05-01', '2023-05-28', '2023-06-23', '2023-06-24', '2023-08-20', '2023-12-24', '2023-12-25', '2023-12-26', '2024-01-01', '2024-02-24', '2024-03-29', '2024-03-31', '2024-05-01', '2024-05-19', '2024-06-23', '2024-06-24', '2024-08-20', '2024-12-24', '2024-12-25', '2024-12-26', '2025-01-01', '2025-02-24', '2025-04-18', '2025-04-20', '2025-05-01', '2025-06-08', '2025-06-23', '2025-06-24', '2025-08-20', '2025-12-24', '2025-12-25', '2025-12-26', '2026-01-01', '2026-02-24', '2026-04-03', '2026-04-05', '2026-05-01', '2026-05-24', '2026-06-23', '2026-06-24', '2026-08-20', '2026-12-24', '2026-12-25', '2026-12-26', '2027-01-01', '2027-02-24', '2027-03-26', '2027-03-28', '2027-05-01', '2027-05-16', '2027-06-23', '2027-06-24', '2027-08-20', '2027-12-24', '2027-12-25', '2027-12-26']

  const day = date.getDay()
  const hours = date.getHours()
  const today = date.toISOString().substring(0, 10)

  switch (service) {
    case 'V1':
      return plans.V1.price
    case 'V5':
      if (holidays.includes(today) || day === 0 || day === 6) {
        if (hours >= 16 || hours < 20) {
          return plans.V5.nightTop
        } else {
          return plans.V5.night
        }
      } else {
        if (hours >= 22 || hours < 7) {
          return plans.V5.night
        } else if ([9, 10, 11, 16, 17, 18, 19].includes(hours)) {
          return plans.V5.dayTop
        } else {
          return plans.V5.day
        }
      }
    default:
      if (holidays.includes(today) || day === 0 || day === 6 || hours >= 22 || hours < 7) {
        return plans[service].night
      } else {
        return plans[service].day
      }
  }
}

async function main (args) {
  const start = new Date()
  const end = new Date()

  end.setDate(end.getDate() + 3)

  const prices = await getPrices(start, end)

  const result = prices.map((p) => {
    const dt = changeTimeZone(new Date(p.timestamp * 1000), 'Europe/Tallinn')
    const price = Math.round(p.price * 10 * 1.2) / 10000
    const gridFee = getGridFee(dt, args.plan)
    const renewableTax = 0.0149
    const excise = 0.0012

    return [
      dt.getFullYear(),
      dt.getMonth() + 1,
      dt.getDate(),
      dt.getHours(),
      price,
      gridFee,
      renewableTax,
      excise
    ]
  })

  return { body: result }
}
