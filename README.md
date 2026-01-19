# Börsihind.ee

Web application for visualizing Estonian electricity exchange prices (Nord Pool) with network fees and taxes.

**Live site**: [borsihind.ee](https://borsihind.ee)

## Features

- **Real-time price visualization** - Interactive charts with 15-minute and 1-hour intervals
- **Network package selection** - Support for V1, V2, V4, V5 packages
- **Price comparison** - Find cheapest time periods for any duration
- **Provider marginal** - Add your electricity provider's markup
- **Price breakdown** - See components: spot price, transmission, taxes, excise
- **Responsive design** - Works on desktop and mobile

## Tech Stack

- **Frontend**: Vue 3 + Vite
- **Charts**: Google Charts
- **Styling**: Tailwind CSS
- **Backend**: AWS Lambda + S3
- **Data**: Nord Pool electricity exchange prices

## API

Public API endpoint: `https://borsihind.s3.eu-central-1.amazonaws.com/`

### Endpoints

- **1-hour intervals**: `/{plan}.json` (e.g., `/V1.json`)
- **15-minute intervals**: `/15min/{plan}.json` (e.g., `/15min/V1.json`)

### Query Parameters

- `plan` - Grid service plan: `V1`, `V2`, `V4`, or `V5`

### Response Format

```json
[
  [
    year,
    month,
    day,
    hour,
    minute,
    electricity_price,
    transmission_fee,
    renewable_tax,
    excise,
    supply_security_fee
  ]
]
```

All prices are in €/MWh (cents per kWh).

## Home Assistant Integration

For Home Assistant users, check out the [HACS integration](https://github.com/argoroots/borsihind) for easy setup with real-time sensors and energy dashboard integration.

## Development

### Project Setup
```sh
npm install
```

### Compile and Hot-Reload for Development
```sh
npm run dev
```

### Compile and Minify for Production
```sh
npm run build
```

### Lint with ESLint
```sh
npm run lint
```

## Credits

[Electricity](https://icons8.com/icon/J4l0714N594x/electricity-hazard) icon by [Icons8](https://icons8.com)

## License

MIT
