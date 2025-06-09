"""Fordpass Switch Entities"""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers.icon import icon_for_battery_level

from . import FordPassEntity
from .const import DOMAIN, SWITCHES, COORDINATOR

_LOGGER = logging.getLogger(__name__)

SWITCHES = {
    "charging": {
        "name": "Charging",
        "icon": "mdi:ev-station"
    },
    "ignition": {
        "name": "Ignition",
        "icon": "mdi:engine"
    },
    "guardmode": {
        "name": "Guard Mode",
        "icon": "mdi:shield"
    },
    "zone_lighting": {
        "name": "Zone Lighting",
        "icon": "mdi:lightbulb-group"
    },
    "zone_front": {
        "name": "Front Zone Light",
        "icon": "mdi:car-light-high"
    },
    "zone_rear": {
        "name": "Rear Zone Light",
        "icon": "mdi:car-light-dimmed"
    },
    "zone_left": {
        "name": "Left Zone Light",
        "icon": "mdi:car-side"
    },
    "zone_right": {
        "name": "Right Zone Light",
        "icon": "mdi:car-side"
    },
    "defrost": {
        "name": "Defrost",
        "icon": "mdi:car-defrost-front"
    },
    "heated_seats": {
        "name": "Heated Seats",
        "icon": "mdi:car-seat-heater"
    },
    "cooled_seats": {
        "name": "Cooled Seats",
        "icon": "mdi:car-seat-cooler"
    }
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Switch from the config."""
    entry = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    switches = []

    # switches = [Switch(entry)]
    # async_add_entities(switches, False)
    for key, value in SWITCHES.items():
        sw = Switch(entry, key, config_entry.options)
        # Only add guard entity if supported by the car
        if key == "guardmode":
            if "guardstatus" in sw.coordinator.data:
                if sw.coordinator.data["guardstatus"]["returnCode"] == 200:
                    async_add_entities([sw], False)
                else:
                    _LOGGER.debug("Guard mode not supported on this vehicle")
        else:
            _LOGGER.debug("Ignition capability not found")

    for key, value in SWITCHES.items():
        sw = Switch(entry, key, config_entry.entry_id)
        _LOGGER.debug("Checking switch %s", key)
        
        # Guard mode switch
        if key == "guardmode":
            if capabilities.get("guardMode") == "Display":
                _LOGGER.debug("Adding guard mode switch")
                switches.append(sw)
        
        # EV charging switch
        elif key == "charging":
            if capabilities.get("globalStartStopCharge") == "Display":
                _LOGGER.debug("Adding charging switch")
                switches.append(sw)
        
        # Zone lighting switches
        elif key.startswith("zone_"):
            if capabilities.get("zoneLighting") == "Display":
                _LOGGER.debug("Adding zone lighting switch %s", key)
                switches.append(sw)
        
        # Climate control switches
        elif key in ["defrost", "heated_seats", "cooled_seats"]:
            if capabilities.get("remoteClimateControl") == "Display":
                if key == "cooled_seats" and vehicle_profile.get("driverHeatedSeat") != "Heat with Vent":
                    continue
                _LOGGER.debug("Adding climate switch %s", key)
                switches.append(sw)

    if switches:
        _LOGGER.debug("Adding switches: %s", [sw.switch for sw in switches])
        async_add_entities(switches, False)


class Switch(FordPassEntity, SwitchEntity):
    """Switch class for FordPass."""

    def __init__(self, coordinator, switch, entry_id):
        """Initialize the Switch class."""
        super().__init__(
            device_id=f"switch_{switch}",
            name=SWITCHES[switch]["name"],
            coordinator=coordinator
        )
        self.switch = switch
        self.coordinator = coordinator
        self.data = coordinator.data["metrics"]
        # Required for HA 2022.7
        self.coordinator_context = object()

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        _LOGGER.debug("Turning on %s", self.switch)
        if self.switch == "ignition":
            await self.coordinator.vehicle.start()
            await self.coordinator.async_request_refresh()
        elif self.switch == "guardmode":
            await self.coordinator.vehicle.enable_guard()
            await self.coordinator.async_request_refresh()
        elif self.switch == "charging":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.ev_start_charge
            )
        elif self.switch == "zone_lighting":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.zone_lighting_activation, None, "On"
            )
        elif self.switch.startswith("zone_"):
            zone = self.switch.replace("zone_", "").capitalize()
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.zone_lighting_zone, None, zone, True
            )
        elif self.switch == "defrost":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle._rcc_update, None, None, None, "On"
            )
        elif self.switch == "heated_seats":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle._rcc_update, None, None, "Heated2", None
            )
        elif self.switch == "cooled_seats":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle._rcc_update, None, None, "Cooled2", None
            )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        _LOGGER.debug("Turning off %s", self.switch)
        if self.switch == "ignition":
            await self.coordinator.vehicle.stop()
            await self.coordinator.async_request_refresh()
        elif self.switch == "guardmode":
            await self.coordinator.vehicle.disable_guard()
            await self.coordinator.async_request_refresh()
        elif self.switch == "charging":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.ev_stop_charge
            )
        elif self.switch == "zone_lighting":
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.zone_lighting_activation, None, "Off"
            )
        elif self.switch.startswith("zone_"):
            zone = self.switch.replace("zone_", "").capitalize()
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle.zone_lighting_zone, None, zone, False
            )
        elif self.switch in ["defrost", "heated_seats", "cooled_seats"]:
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.vehicle._rcc_update, None, None, "Off", "Off"
            )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Check status of switch - considers both ignition and remote start status"""
        if self.switch == "ignition":
            if self.coordinator.data["metrics"] is None:
                return None
            
            # Check ignition status first
            ignition_status = None
            if (self.coordinator.data["metrics"].get("ignitionStatus") is not None):
                ignition_status = self.coordinator.data["metrics"]["ignitionStatus"]["value"]
                _LOGGER.debug(f"Ignition status: {ignition_status}")
            
            # Check remote start status using multiple methods
            remote_start_active = False
            
            # Method 1: Check countdown timer (most reliable)
            if "remoteStartCountdownTimer" in self.coordinator.data["metrics"]:
                countdown_timer = self.coordinator.data["metrics"]["remoteStartCountdownTimer"].get("value", 0)
                if countdown_timer and countdown_timer > 0:
                    remote_start_active = True
                    _LOGGER.debug(f"Remote start active via countdown timer: {countdown_timer}")
            
            
            # Vehicle is "on" if either ignition is on OR remote start is active
            if remote_start_active:
                _LOGGER.debug("Vehicle is ON via remote start")
                return True
            elif ignition_status in ["ON", "RUN", "START", "ACCESSORY"]:
                _LOGGER.debug("Vehicle is ON via ignition")
                return True
            elif ignition_status == "OFF":
                _LOGGER.debug("Vehicle is OFF")
                return False
            elif ignition_status is None:
                # If we can't get ignition status, fall back to remote start only
                _LOGGER.debug(f"No ignition status available, using remote start status: {remote_start_active}")
                return remote_start_active
            else:
                _LOGGER.warning(f"Unknown ignition status: {ignition_status}, using remote start status: {remote_start_active}")
                return remote_start_active  # Fall back to remote start status
                
        elif self.switch == "guardmode":
            # Guard mode logic remains the same
            guardstatus = self.coordinator.data.get("guardstatus", {})
            _LOGGER.debug(f"Guard status: {guardstatus}")
            
            if guardstatus.get("returnCode") == 200:
                if "session" in guardstatus and "gmStatus" in guardstatus["session"]:
                    if guardstatus["session"]["gmStatus"] == "enable":
                        return True
                    elif guardstatus["session"]["gmStatus"] == "disable":
                        return False
                return False
            return False
        
        return False

    @property
    def icon(self):
        """Return icon for switch"""
        return SWITCHES[self.switch]["icon"]
