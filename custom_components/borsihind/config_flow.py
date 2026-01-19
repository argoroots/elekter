"""Config flow for Börsihind.ee integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_MARGINAL, CONF_PLAN, CONF_INTERVAL, DOMAIN, PLANS, INTERVALS


class BorsihindConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Börsihind.ee."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(f"borsihind_{user_input[CONF_PLAN]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Börsihind.ee {PLANS[user_input[CONF_PLAN]]}",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PLAN, default="V1"): vol.In(PLANS),
                vol.Required(CONF_INTERVAL, default="15min"): vol.In(INTERVALS),
                vol.Optional(CONF_MARGINAL, default=0.0): vol.All(
                    vol.Coerce(float), vol.Range(min=0.0, max=100.0)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BorsihindOptionsFlow:
        """Get the options flow for this handler."""
        return BorsihindOptionsFlow()


class BorsihindOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Börsihind.ee."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_INTERVAL,
                            self.config_entry.data.get(CONF_INTERVAL, "15min"),
                        ),
                    ): vol.In(INTERVALS),
                    vol.Optional(
                        CONF_MARGINAL,
                        default=self.config_entry.options.get(
                            CONF_MARGINAL,
                            self.config_entry.data.get(CONF_MARGINAL, 0.0),
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=100.0)),
                }
            ),
        )
