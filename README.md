# Börsihind.ee

API and website to get hourly electricity price.
API query parameters:
- plan - Grid service plan: V1, V2, V2k, V4 or V5.

API response is in following format:
```
  [
    year,
    month,
    day,
    hour,
    price,
    gridFee,
    renewableTax,
    excise
  ]
```

[Electricity](https://icons8.com/icon/J4l0714N594x/electricity-hazard) icon by [Icons8](https://icons8.com)


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

### Lint with [ESLint](https://eslint.org/)
```sh
npm run lint
```
