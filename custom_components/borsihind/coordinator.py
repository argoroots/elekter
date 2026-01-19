"""Data update coordinator for Börsihind.ee."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, CONF_MARGINAL, CONF_PLAN, CONF_INTERVAL, DOMAIN, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


class ElektrilviCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching electricity price data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.plan = entry.data[CONF_PLAN]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    @property
    def interval(self) -> str:
        """Get interval value from options or data."""
        return self.entry.options.get(
            CONF_INTERVAL, self.entry.data.get(CONF_INTERVAL, "15min")
        )

    @property
    def marginal(self) -> float:
        """Get marginal value from options or data."""
        return self.entry.options.get(
            CONF_MARGINAL, self.entry.data.get(CONF_MARGINAL, 0)
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        interval_path = "" if self.interval == "1h" else "15min/"
        url = f"{API_URL}/{interval_path}{self.plan}.json"

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error fetching data: {response.status}")

                        data = await response.json()
                        return self._process_data(data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _process_data(self, raw_data: list) -> dict[str, Any]:
        """Process raw API data into usable format."""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        current_interval = (current_minute // 15) * 15
        is_1h = self.interval == "1h"

        prices = []
        for item in raw_data:
            price_year = item[0]
            price_month = item[1]
            price_day = item[2]
            price_hour = item[3]
            price_minute = item[4]

            # Create date objects for comparison
            price_date = datetime(price_year, price_month, price_day, price_hour, price_minute)
            current_date = datetime(
                now.year, now.month, now.day,
                current_hour,
                0 if is_1h else current_interval
            )

            # Filter: keep entries that are at or after the current time
            if price_date < current_date:
                continue

            prices.append({
                "time": f"{str(price_hour).zfill(2)}:{str(price_minute).zfill(2)}",
                "hour": price_hour,
                "minute": price_minute,
                "excise": item[8] * 100,
                "supply_security": item[9] * 100,
                "renewable": item[7] * 100,
                "transmission": item[6] * 100,
                "electricity": item[5] * 100,
                "year": price_year,
                "month": price_month,
                "day": price_day,
            })

        if not prices:
            raise UpdateFailed("No price data available for current time")

        # Calculate total price with marginal for each entry
        for price in prices:
            price["total"] = (
                self.marginal
                + price["excise"]
                + price["supply_security"]
                + price["renewable"]
                + price["transmission"]
                + price["electricity"]
            )

        # Find current price (first in filtered list)
        current_price = prices[0]

        # Calculate averages for future prices
        future_prices = [p["total"] for p in prices]
        avg_price = sum(future_prices) / len(future_prices) if future_prices else 0

        # Find min and max
        min_price = min(future_prices) if future_prices else 0
        max_price = max(future_prices) if future_prices else 0

        return {
            "current": current_price,
            "prices": prices,
            "average": avg_price,
            "min": min_price,
            "max": max_price,
            "last_update": now,
        }
