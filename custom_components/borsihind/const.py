"""Constants for the Börsihind.ee integration."""

DOMAIN = "borsihind"

# Configuration
CONF_PLAN = "plan"
CONF_MARGINAL = "marginal"
CONF_INTERVAL = "interval"

# Plans
PLANS = {
    "V1": "Võrk 1",
    "V2": "Võrk 2",
    "V4": "Võrk 4",
    "V5": "Võrk 5",
}
Intervals
INTERVALS = {
    "15min": "15 minutit",
    "1h": "1 tund",
}

#
# API
API_URL = "https://borsihind.s3.eu-central-1.amazonaws.com"

# Update interval
UPDATE_INTERVAL_MINUTES = 15
