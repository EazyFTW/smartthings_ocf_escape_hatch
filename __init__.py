"""Parasitic integration for sending raw OCF requests to SmartThings media players."""

import typing as t

from pysmartthings import Capability, Command

from homeassistant.components.smartthings import SmartThingsData
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr, entity_registry as er


async def async_setup(hass: HomeAssistant, _):
    """Attach the brain slug."""

    async def do_ocf_post(call: ServiceCall):
        entity_ids: list[str] = call.data['entity_id']
        path: str = call.data['path']
        params: dict[t.Any, t.Any] = call.data['params']

        dev_reg = dr.async_get(hass)
        ent_reg = er.async_get(hass)

        for entity_id in entity_ids:
            entity = ent_reg.async_get(entity_id)
            assert entity
            assert entity.config_entry_id
            assert entity.device_id

            device = dev_reg.async_get(entity.device_id)
            assert device

            device_id = None
            for (domain, id_) in device.identifiers:
                if domain == "smartthings":
                    device_id = id_

            assert device_id

            integration = hass.config_entries.async_get_known_entry(entity.config_entry_id)
            data: SmartThingsData = t.cast("SmartThingsData", integration.runtime_data)

            await data.client.execute_device_command(
                device_id,
                Capability.EXECUTE,
                Command.EXECUTE,
                argument=[path, params],
            )

    hass.services.async_register(
        "smartthings_ocf_escape_hatch",
        "ocf_post",
        do_ocf_post,
    )

    return True
