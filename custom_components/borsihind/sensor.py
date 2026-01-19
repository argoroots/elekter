"""Sensor platform for Börsihind.ee."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PLAN, DOMAIN, PLANS
from .coordinator import ElektrilviCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Börsihind.ee sensor entities."""
    coordinator: ElektrilviCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            ElektrilviCurrentPriceSensor(coordinator, entry),
            ElektrilviAveragePriceSensor(coordinator, entry),
            ElektrilviMinPriceSensor(coordinator, entry),
            ElektrilviMaxPriceSensor(coordinator, entry),
        ]
    )


class ElektrilviSensorBase(CoordinatorEntity[ElektrilviCoordinator], SensorEntity):
    """Base class for Börsihind.ee sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ElektrilviCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Börsihind.ee {PLANS[entry.data[CONF_PLAN]]}",
            "manufacturer": "Börsihind.ee",
            "model": PLANS[entry.data[CONF_PLAN]],
        }


class ElektrilviCurrentPriceSensor(ElektrilviSensorBase):
    """Sensor for current electricity price."""

    _attr_name = "Current Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: ElektrilviCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_price"

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        if self.coordinator.data and "current" in self.coordinator.data:
            # Convert from cents to euros
            return round(self.coordinator.data["current"]["total"] / 100, 4)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if not self.coordinator.data or "current" not in self.coordinator.data:
            return {}

        current = self.coordinator.data["current"]
        return {
            "time": current["time"],
            "electricity_price": round(current["electricity"] / 100, 4),
            "transmission": round(current["transmission"] / 100, 4),
            "renewable_tax": round(current["renewable"] / 100, 4),
            "supply_security": round(current["supply_security"] / 100, 4),
            "excise": round(current["excise"] / 100, 4),
            "marginal": round(self.coordinator.marginal / 100, 4),
            "prices": [
                {
                    "time": p["time"],
                    "price": round(p["total"] / 100, 4),
                }
                for p in self.coordinator.data.get("prices", [])[:24]
            ],
        }


class ElektrilviAveragePriceSensor(ElektrilviSensorBase):
    """Sensor for average future electricity price."""

    _attr_name = "Average Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: ElektrilviCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_average_price"

    @property
    def native_value(self) -> float | None:
        """Return the average price."""
        if self.coordinator.data and "average" in self.coordinator.data:
            # Convert from cents to euros
            return round(self.coordinator.data["average"] / 100, 4)
        return None


class ElektrilviMinPriceSensor(ElektrilviSensorBase):
    """Sensor for minimum future electricity price."""

    _attr_name = "Minimum Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: ElektrilviCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_min_price"

    @property
    def native_value(self) -> float | None:
        """Return the minimum price."""
        if self.coordinator.data and "min" in self.coordinator.data:
            # Convert from cents to euros
            return round(self.coordinator.data["min"] / 100, 4)
        return None


class ElektrilviMaxPriceSensor(ElektrilviSensorBase):
    """Sensor for maximum future electricity price."""

    _attr_name = "Maximum Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: ElektrilviCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_max_price"

    @property
    def native_value(self) -> float | None:
        """Return the maximum price."""
        if self.coordinator.data and "max" in self.coordinator.data:
            # Convert from cents to euros
            return round(self.coordinator.data["max"] / 100, 4)
        return None
