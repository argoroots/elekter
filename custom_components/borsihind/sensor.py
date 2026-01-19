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
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PLAN, DOMAIN, PLANS, INTERVALS
from .coordinator import BorsihindCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Börsihind.ee sensor entities."""
    coordinator: BorsihindCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            BorsihindCurrentPriceSensor(coordinator, entry),
            BorsihindAveragePriceSensor(coordinator, entry),
            BorsihindMinPriceSensor(coordinator, entry),
            BorsihindMaxPriceSensor(coordinator, entry),
            BorsihindPlanSensor(coordinator, entry),
            BorsihindIntervalSensor(coordinator, entry),
            BorsihindMarginalSensor(coordinator, entry),
        ]
    )


class BorsihindSensorBase(CoordinatorEntity[BorsihindCoordinator], SensorEntity):
    """Base class for Börsihind.ee sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
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


class BorsihindCurrentPriceSensor(BorsihindSensorBase):
    """Sensor for current electricity price."""

    _attr_name = "Current Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
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


class BorsihindAveragePriceSensor(BorsihindSensorBase):
    """Sensor for average future electricity price."""

    _attr_name = "Average Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
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


class BorsihindMinPriceSensor(BorsihindSensorBase):
    """Sensor for minimum future electricity price."""

    _attr_name = "Minimum Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
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


class BorsihindMaxPriceSensor(BorsihindSensorBase):
    """Sensor for maximum future electricity price."""

    _attr_name = "Maximum Price"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
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


class BorsihindPlanSensor(BorsihindSensorBase):
    """Sensor for network package configuration."""

    _attr_name = "Network Package"
    _attr_icon = "mdi:package-variant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_plan"

    @property
    def native_value(self) -> str | None:
        """Return the network package."""
        plan = self.coordinator.entry.options.get(
            CONF_PLAN,
            self.coordinator.entry.data.get(CONF_PLAN)
        )
        return f"{plan} - {PLANS.get(plan, plan)}" if plan else None


class BorsihindIntervalSensor(BorsihindSensorBase):
    """Sensor for data interval configuration."""

    _attr_name = "Data Interval"
    _attr_icon = "mdi:clock-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_interval"

    @property
    def native_value(self) -> str | None:
        """Return the data interval."""
        return self.coordinator.interval


class BorsihindMarginalSensor(BorsihindSensorBase):
    """Sensor for provider marginal configuration."""

    _attr_name = "Provider Marginal"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: BorsihindCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_marginal"

    @property
    def native_value(self) -> float | None:
        """Return the provider marginal."""
        # Convert from cents to euros
        return round(self.coordinator.marginal / 100, 4)
