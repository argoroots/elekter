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

function getGridFee (date) {
  const gridFeeDay = 0.0443
  const gridFeeNight = 0.0252
  const holidays = ['2023-05-01', '2023-05-14', '2023-05-28', '2023-06-04', '2023-06-14', '2023-06-22', '2023-06-23', '2023-06-24', '2023-08-20', '2023-08-23', '2023-09-10', '2023-09-22', '2023-10-21', '2023-11-02', '2023-11-12', '2023-11-16', '2023-12-23', '2023-12-24', '2023-12-25', '2023-12-26', '2023-12-31', '2024-01-01', '2024-01-06', '2024-02-02', '2024-02-23', '2024-02-24', '2024-03-14', '2024-03-29', '2024-03-31', '2024-05-01', '2024-05-12', '2024-05-19', '2024-06-04', '2024-06-14', '2024-06-22', '2024-06-23', '2024-06-24', '2024-08-20', '2024-08-23', '2024-09-08', '2024-09-22', '2024-10-19', '2024-11-02', '2024-11-10', '2024-11-16', '2024-12-23', '2024-12-24', '2024-12-25', '2024-12-26', '2024-12-31', '2025-01-01', '2025-01-06', '2025-02-02', '2025-02-23', '2025-02-24', '2025-03-14', '2025-04-18', '2025-04-20', '2025-05-01', '2025-05-11', '2025-06-04', '2025-06-08', '2025-06-14', '2025-06-22', '2025-06-23', '2025-06-24', '2025-08-20', '2025-08-23', '2025-09-14', '2025-09-22', '2025-10-18', '2025-11-02', '2025-11-09', '2025-11-16', '2025-12-23', '2025-12-24', '2025-12-25', '2025-12-26', '2025-12-31', '2026-01-01', '2026-01-06', '2026-02-02', '2026-02-23', '2026-02-24', '2026-03-14', '2026-04-03', '2026-04-05', '2026-05-01', '2026-05-10', '2026-05-24', '2026-06-04', '2026-06-14', '2026-06-22', '2026-06-23', '2026-06-24', '2026-08-20', '2026-08-23', '2026-09-13', '2026-09-22', '2026-10-17', '2026-11-02', '2026-11-08', '2026-11-16', '2026-12-23', '2026-12-24', '2026-12-25', '2026-12-26', '2026-12-31', '2027-01-01', '2027-01-06', '2027-02-02', '2027-02-23', '2027-02-24', '2027-03-14', '2027-03-26', '2027-03-28', '2027-05-01', '2027-05-09', '2027-05-16', '2027-06-04', '2027-06-14', '2027-06-22', '2027-06-23', '2027-06-24', '2027-08-20', '2027-08-23', '2027-09-12', '2027-09-22', '2027-10-16', '2027-11-02', '2027-11-14', '2027-11-16', '2027-12-23', '2027-12-24', '2027-12-25', '2027-12-26', '2027-12-31']

  const day = date.getDay()
  const hours = date.getHours()
  const today = date.toISOString().substring(0, 10)

  if (holidays.includes(today)) return gridFeeNight
  if (day === 0 || day === 6) return gridFeeNight
  if (hours >= 22 || hours < 7) return gridFeeNight

  return gridFeeDay
}

exports.handler = async (event) => {
  const start = new Date()
  const end = new Date()

  end.setDate(end.getDate() + 3)

  const prices = await getPrices(start, end)

  const result = prices.map((p) => {
    const dt = changeTimeZone(new Date(p.timestamp * 1000), 'Europe/Tallinn')
    const price = Math.round(p.price * 10 * 1.2) / 10000
    const gridFee = getGridFee(dt)
    const renewableTax = 0.0149
    const excise = 0.0012
    const total = Math.round((price + gridFee + renewableTax + excise) * 10000) / 10000

    return [
      dt.getFullYear(),
      dt.getMonth() + 1,
      dt.getDate(),
      dt.getHours(),
      price,
      gridFee,
      renewableTax,
      excise,
      total
    ]
  })

  return result
}
