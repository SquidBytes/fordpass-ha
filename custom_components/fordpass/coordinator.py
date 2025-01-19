import logging

_LOGGER = logging.getLogger(__name__)

class Coordinator:
    async def _async_update_data(self):
        """Update data via library."""
        data = await self.hass.async_add_executor_job(self.vehicle.status)
        _LOGGER.debug("Coordinator data: %s", data)
        return data 