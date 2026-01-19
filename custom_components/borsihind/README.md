# Börsihind.ee - Home Assistant Integration

Home Assistant integration for Estonian electricity exchange prices (Nord Pool) with network fees.

## Features

- **Real-time electricity prices** - Current price with all components (electricity, transmission, taxes, marginal)
- **Price forecasting** - See future prices and plan energy usage
- **Energy dashboard integration** - Automatic cost calculation for your energy consumption
- **Multiple network packages** - Support for V1, V2, V4, V5 packages
- **Flexible data intervals** - Choose between 15-minute or 1-hour intervals
- **Configurable marginal** - Add your electricity provider's markup

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/argoroots/borsihind`
6. Category: Integration
7. Click "Add"
8. Find "Börsihind.ee" and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the integration folder to your Home Assistant's `custom_components/borsihind` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Börsihind.ee"
4. Select your network package (V1, V2, V4, or V5)
5. Choose data interval (15 minutes or 1 hour)
6. Enter your electricity provider's marginal (optional, default: 0)

You can later adjust the interval and marginal in the integration's options without removing it.

## Sensors

The integration provides 4 sensors:

- **Current Price** - Current electricity price (€/kWh) with all fees included
  - Attributes include breakdown of all price components
  - Includes future prices for automation
- **Average Price** - Average of all future prices
- **Minimum Price** - Lowest upcoming price
- **Maximum Price** - Highest upcoming price

## Energy Dashboard Integration

To use with Home Assistant's Energy dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Under "Electricity grid" → "Add consumption"
3. Select your energy meter entity
4. For "Use an entity tracking the total costs", select **No**
5. For "Use an entity with the current price", select **Yes**
6. Choose the **Current Price** sensor from this integration

Home Assistant will now automatically calculate your energy costs using real-time prices!

## Automation Examples

### Get notified when price drops below average

```yaml
automation:
  - alias: "Low electricity price notification"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.borsihind_ee_vork_1_current_price') | float <
             states('sensor.borsihind_ee_vork_1_average_price') | float }}
    action:
      - service: notify.mobile_app
        data:
          message: "Electricity price is below average! Good time to use energy-intensive appliances."
```

### Turn on water heater during cheapest hours

```yaml
automation:
  - alias: "Smart water heater control"
    trigger:
      - platform: time_pattern
        minutes: "/15"
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.borsihind_ee_vork_1_current_price') | float ==
             states('sensor.borsihind_ee_vork_1_minimum_price') | float }}
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.water_heater
```
Nord Pool via `https://borsihind.s3.eu-central-1.amazonaws.com/`
- Update interval: 15 minutes
- Data intervals: 15-minute or 1-hour (user selectable)
- Data includes: Electricity price, transmission fees, renewable energy tax, supply security fee, excise tax
- Prices are filtered to show only current and future time periods
- All prices include 24% VATcom/`
- Update interval: 15 minutes
- Data includes: Electricity price, transmission fees, renewable energy tax, supply security fee, excise tax
- Prices are filtered to show only current and future prices

## Price Components24% VAT and are shown in €/kWh:

1. **Electricity price** - Nord Pool exchange price
2. **Transmission** - Network transmission fee (varies by package and time)
3. **Renewable tax** - Renewable energy tax (1.04 c/kWh)
4. **Supply security** - Supply security fee (0.94 c/kWh)
5. **Excise** - Electricity excise tax (0.26 c/kWh)y tax
4. **Supply security** - Supply security fee
5. **Excise** - Electricity excise tax
6. **Marginal** - Your provider's markup (configurable)

## Support

For issues, questions, or feature requests, please visit:
- GitHub: https://github.com/argoroots/borsihind/issues
- Email: argo@roots.ee

## Credits

Data provided by Nord Pool. Based on [Börsihind.ee](https://borsihind.ee):argo@roots.ee)

Based on the Elektri Börsihind web application.
