const { S3Client, PutObjectCommand, PutObjectAclCommand, PutObjectTaggingCommand } = require('@aws-sdk/client-s3')

async function getPrices () {
  const start = new Date()
  const currentDate = start.toISOString().substring(0, 10)
  const nextDate = new Date(start)
  nextDate.setDate(nextDate.getDate() + 1)
  const nextDateStr = nextDate.toISOString().substring(0, 10)

  const allEntries = []

  // Make request for current day
  try {
    const currentResponse = await fetch(`https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices?currency=EUR&market=DayAhead&deliveryArea=EE&date=${currentDate}`)
    const currentData = await currentResponse.json()

    if (currentData?.multiAreaEntries) {
      allEntries.push(...currentData.multiAreaEntries)
    }
  } catch (error) {
    console.error('Error fetching prices for current day:', error)
  }

  // Make request for next day
  try {
    const nextResponse = await fetch(`https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices?currency=EUR&market=DayAhead&deliveryArea=EE&date=${nextDateStr}`)
    const nextData = await nextResponse.json()

    if (nextData?.multiAreaEntries) {
      allEntries.push(...nextData.multiAreaEntries)
    }
  } catch (error) {
    console.error('Error fetching prices for next day:', error)
  }

  // Filter out past 15-minute intervals - only keep current interval and future intervals
  const now = new Date()
  const currentInterval = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), Math.floor(now.getMinutes() / 15) * 15)
  return allEntries.filter(entry => new Date(entry.deliveryStart) >= currentInterval)
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
      price: 0.0957
    },
    V2: {
      day: 0.0753,
      night: 0.0435
    },
    V4: {
      day: 0.0458,
      night: 0.0260

    },
    V5: {
      day: 0.0656,
      dayTop: 0.1014,
      night: 0.0376,
      nightTop: 0.0588
    }
  }
  const holidays = ['2025-08-20', '2025-12-24', '2025-12-25', '2025-12-26', '2026-01-01', '2026-02-24', '2026-04-03', '2026-04-05', '2026-05-01', '2026-05-24', '2026-06-23', '2026-06-24', '2026-08-20', '2026-12-24', '2026-12-25', '2026-12-26', '2027-01-01', '2027-02-24', '2027-03-26', '2027-03-28', '2027-05-01', '2027-05-16', '2027-06-23', '2027-06-24', '2027-08-20', '2027-12-24', '2027-12-25', '2027-12-26']

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
      } else if (hours >= 22 || hours < 7) {
        return plans.V5.night
      } else if ([9, 10, 11, 16, 17, 18, 19].includes(hours)) {
        return plans.V5.dayTop
      } else {
        return plans.V5.day
      }
    default:
      if (holidays.includes(today) || day === 0 || day === 6 || hours >= 22 || hours < 7) {
        return plans[service].night
      } else {
        return plans[service].day
      }
  }
}

async function saveJSON (prices, plan) {
  const result = prices.map((p) => {
    const dt = changeTimeZone(new Date(p.deliveryStart), 'Europe/Tallinn')
    const price = Math.round(p.entryPerArea.EE * 1.24 / 1000 * 10000) / 10000
    const gridFee = getGridFee(dt, plan)
    const renewableTax = 0.0104
    const excise = 0.0026

    return [
      dt.getFullYear(),
      dt.getMonth() + 1,
      dt.getDate(),
      dt.getHours(),
      dt.getMinutes(),
      price,
      gridFee,
      renewableTax,
      excise
    ]
  })

  const jsonResult = JSON.stringify(result)
  const bucketName = 'argoroots-public'
  const key = `borsihind/${plan}.json`

  const s3Client = new S3Client({
    region: process.env.S3_REGION,
    credentials: {
      accessKeyId: process.env.S3_ACCESS_KEY,
      secretAccessKey: process.env.S3_SECRET_KEY
    }
  })

  await s3Client.send(new PutObjectCommand({
    Bucket: bucketName,
    Key: key,
    Body: jsonResult,
    ContentType: 'application/json'
  }))

  await s3Client.send(new PutObjectAclCommand({
    Bucket: bucketName,
    Key: key,
    ACL: 'public-read'
  }))

  await s3Client.send(new PutObjectTaggingCommand({
    Bucket: bucketName,
    Key: key,
    Tagging: {
      TagSet: [{ Key: 'Project', Value: 'borsihind' }]
    }
  }))
}

async function main () {
  const plans = ['V1', 'V2', 'V4', 'V5']

  const prices = await getPrices()

  if (prices.length === 0) {
    console.log('No prices data available, skipping file write')
    return { ok: false, message: 'No data to save' }
  }

  for (const plan of plans) {
    await saveJSON(prices, plan)
  }

  return { ok: true }
}
