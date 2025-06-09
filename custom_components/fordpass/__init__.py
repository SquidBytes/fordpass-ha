"""The FordPass integration."""
import asyncio
import logging
from datetime import timedelta

import async_timeout
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.storage import Store

from .const import (
    CONF_DISTANCE_UNIT,
    CONF_PRESSURE_UNIT,
    DEFAULT_DISTANCE_UNIT,
    DEFAULT_PRESSURE_UNIT,
    DEFAULT_REGION,
    DOMAIN,
    MANUFACTURER,
    REGION,
    VEHICLE,
    VIN,
    UPDATE_INTERVAL,
    UPDATE_INTERVAL_DEFAULT,
    COORDINATOR,
    STORAGE_VERSION,
    STORAGE_KEY_PREFIX,
)
from .fordpass_new import Vehicle

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["lock", "sensor", "switch", "device_tracker"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the FordPass component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ford Pass from a config entry."""
    user = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    vin = entry.data[VIN]
    if UPDATE_INTERVAL in entry.options:
        update_interval = entry.options[UPDATE_INTERVAL]
    else:
        update_interval = UPDATE_INTERVAL_DEFAULT
    _LOGGER.debug(update_interval)
    for ar_entry in entry.data:
        _LOGGER.debug(ar_entry)
    if REGION in entry.data.keys():
        _LOGGER.debug(entry.data[REGION])
        region = entry.data[REGION]
    else:
        _LOGGER.debug("CANT GET REGION")
        region = DEFAULT_REGION
<<<<<<< HEAD
    coordinator = FordPassDataUpdateCoordinator(hass, user, password, vin, region, update_interval, 1)
=======
    
    # Create token store for this user
    token_store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}_{user}")
    
    coordinator = FordPassDataUpdateCoordinator(
        hass, user, password, vin, region, update_interval, token_store
    )
>>>>>>> bc1b34f4b41caf7294c6c8320cc281cb3f2fc542

    await coordinator.async_refresh()  # Get initial data

    fordpass_options_listener = entry.add_update_listener(options_update_listener)

    if not entry.options:
        await async_update_options(hass, entry)

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        "fordpass_options_listener": fordpass_options_listener
    }

<<<<<<< HEAD
    await hass.config_entries.async_forward_entry_setups(
        entry, ["device_tracker", "sensor", "switch", "lock"]
    )

    async def async_refresh_status_service(service_call):
        await hass.async_add_executor_job(
            refresh_status, hass, service_call, coordinator
        )
=======
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_refresh_status_service(service_call):
        """Handle refresh status for specific VIN or all vehicles"""
        target_vin = service_call.data.get("vin", "")
        
        if target_vin:
            # Refresh specific vehicle
            _LOGGER.debug(f"Refreshing status for VIN: {target_vin}")
            try:
                # Use the async request_update method directly
                result = await coordinator.vehicle.request_update(target_vin)
                if result:
                    _LOGGER.debug("Refresh command succeeded, updating coordinator data")
                    # Wait a moment for the vehicle to process the command
                    await asyncio.sleep(2)
                    # Force refresh the coordinator data
                    await coordinator.async_request_refresh()
                else:
                    _LOGGER.warning("Refresh command failed")
            except Exception as e:
                _LOGGER.error(f"Error during refresh: {e}")
        else:
            # Refresh all vehicles for this account
            all_entries = hass.config_entries.async_entries(DOMAIN)
            current_username = entry.data[CONF_USERNAME]
            
            for config_entry in all_entries:
                if config_entry.data.get(CONF_USERNAME) == current_username:
                    entry_coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
                    _LOGGER.debug(f"Refreshing status for VIN: {entry_coordinator.vin}")
                    try:
                        # Use the async request_update method directly
                        result = await entry_coordinator.vehicle.request_update()
                        if result:
                            _LOGGER.debug("Refresh command succeeded, updating coordinator data")
                            # Wait a moment for the vehicle to process the command
                            await asyncio.sleep(2)
                            # Force refresh the coordinator data
                            await entry_coordinator.async_request_refresh()
                        else:
                            _LOGGER.warning(f"Refresh command failed for VIN: {entry_coordinator.vin}")
                    except Exception as e:
                        _LOGGER.error(f"Error during refresh for VIN {entry_coordinator.vin}: {e}")
>>>>>>> bc1b34f4b41caf7294c6c8320cc281cb3f2fc542

    async def async_clear_tokens_service(service_call):
        """Clear tokens for this user account"""
        await coordinator.vehicle.clear_token()

    async def poll_api_service(service_call):
        """Poll API for this vehicle"""
        await coordinator.async_request_refresh()

    async def handle_reload(service):
        """Handle reload service call."""
        _LOGGER.debug("Reloading Integration")

        current_entries = hass.config_entries.async_entries(DOMAIN)
        reload_tasks = [
            hass.config_entries.async_reload(entry.entry_id)
            for entry in current_entries
        ]

        await asyncio.gather(*reload_tasks)

    async def async_get_charge_logs_service(service_call):
        """Handle getting charge logs service call."""
        try:
            vin = service_call.data.get("vin", "")
            coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
            
            _LOGGER.debug("Starting charge logs service call")
            _LOGGER.debug("VIN: %s", vin)
            
            logs = await hass.async_add_executor_job(
                coordinator.vehicle.ev_energy_transfer_logs
            )
            
            _LOGGER.debug("Received logs: %s", logs)
            
            if logs:
                result = {
                    "charge_logs": logs,
                    "success": True,
                    "message": "Successfully retrieved charge logs"
                }
                _LOGGER.debug("Returning successful result: %s", result)
                return result
            else:
                result = {
                    "success": False,
                    "message": "No charge logs retrieved or vehicle doesn't support charging logs"
                }
                _LOGGER.debug("Returning failed result: %s", result)
                return result
                
        except Exception as ex:
            _LOGGER.error("Service error: %s", str(ex))
            _LOGGER.debug("Service error details:", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(ex)}"
            }

    # Register all services
    hass.services.async_register(
        DOMAIN,
        "refresh_status",
        async_refresh_status_service,
    )
    
    hass.services.async_register(
        DOMAIN,
        "clear_tokens",
        async_clear_tokens_service,
    )

    hass.services.async_register(
        DOMAIN,
        "reload",
        handle_reload
    )

    hass.services.async_register(
        DOMAIN,
        "poll_api",
        poll_api_service
    )

    # Register our new charge logs service
    hass.services.async_register(
        DOMAIN,
        "get_charge_logs",
        async_get_charge_logs_service
    )

    return True


async def async_update_options(hass, config_entry):
    """Update options entries on change"""
    options = {
        CONF_PRESSURE_UNIT: config_entry.data.get(
            CONF_PRESSURE_UNIT, DEFAULT_PRESSURE_UNIT
        )
    }
    options[CONF_DISTANCE_UNIT] = config_entry.data.get(
        CONF_DISTANCE_UNIT, DEFAULT_DISTANCE_UNIT
    )
    hass.config_entries.async_update_entry(config_entry, options=options)


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Options listener to refresh config entries on option change"""
    _LOGGER.debug("OPTIONS CHANGE")
    await hass.config_entries.async_reload(entry.entry_id)

<<<<<<< HEAD

def refresh_status(hass, service, coordinator):
    """Get latest vehicle status from vehicle, actively polls the car"""
    _LOGGER.debug("Running Service")
    vin = service.data.get("vin", "")
    status = coordinator.vehicle.request_update(vin)
    if status == 401:
        _LOGGER.debug("Invalid VIN")
    elif status == 200:
        _LOGGER.debug("Refresh Sent")


def clear_tokens(hass, service, coordinator):
    """Clear the token file in config directory, only use in emergency"""
    _LOGGER.debug("Clearing Tokens")
    coordinator.vehicle.clear_token()


=======
>>>>>>> bc1b34f4b41caf7294c6c8320cc281cb3f2fc542
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False


class FordPassDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to handle fetching new data about the vehicle."""

    def __init__(self, hass, user, password, vin, region, update_interval, token_store):
        """Initialize the coordinator and set up the Vehicle object."""
        self._hass = hass
        self.vin = vin
        self.vehicle = Vehicle(user, password, vin, region, token_store, hass)
        self._available = True

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        """Fetch data from FordPass."""
        try:
            async with async_timeout.timeout(30):
                data = await self.vehicle.status()

                # Temporarily removed due to Ford backend API changes
                # data["guardstatus"] = await self.vehicle.guardStatus()

                data["messages"] = await self.vehicle.messages()
                data["vehicles"] = await self.vehicle.vehicles()
                _LOGGER.debug(data)
                # If data has now been fetched but was previously unavailable, log and reset
                if not self._available:
                    _LOGGER.info("Restored connection to FordPass for %s", self.vin)
                    self._available = True

                return data
        except Exception as ex:
            self._available = False  # Mark as unavailable
            _LOGGER.warning(str(ex))
            _LOGGER.warning("Error communicating with FordPass for %s", self.vin)
            raise UpdateFailed(
                f"Error communicating with FordPass for {self.vin}"
            ) from ex


class FordPassEntity(CoordinatorEntity):
    """Defines a base FordPass entity."""

    def __init__(
        self, *, device_id: str, name: str, coordinator: FordPassDataUpdateCoordinator
    ):
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._name = name

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the entity."""
        return f"{self.coordinator.vin}-{self._device_id}"

    @property
    def device_info(self):
        """Return device information about this device."""
        if self._device_id is None:
            return None

        model = "unknown"
        if self.coordinator.data["vehicles"] is not None:
            for vehicle in self.coordinator.data["vehicles"]["vehicleProfile"]:
                if vehicle["VIN"] == self.coordinator.vin:
                    model = f"{vehicle['year']} {vehicle['model']}"

        return {
            "identifiers": {(DOMAIN, self.coordinator.vin)},
            "name": f"{VEHICLE} ({self.coordinator.vin})",
            "model": f"{model}",
            "manufacturer": MANUFACTURER,
        }