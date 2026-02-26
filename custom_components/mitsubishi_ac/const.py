"""Constants for the Mitsubishi AC integration."""

from homeassistant.components.climate import HVACMode

DOMAIN = "mitsubishi_ac"

DEFAULT_PORT = 80
ENDPOINT_PATH = "/servlet/MIMEReceiveServlet"
SCAN_INTERVAL_SECONDS = 30

# Controller mode -> HA HVACMode
MODE_TO_HVAC: dict[str, HVACMode] = {
    "COOL": HVACMode.COOL,
    "HEAT": HVACMode.HEAT,
    "DRY": HVACMode.DRY,
    "FAN": HVACMode.FAN_ONLY,
    "AUTO": HVACMode.HEAT_COOL,
    "LC_AUTO": HVACMode.HEAT_COOL,
    "AUTOHEAT": HVACMode.HEAT_COOL,
    "AUTOCOOL": HVACMode.HEAT_COOL,
}

# HA HVACMode -> controller mode
HVAC_TO_MODE: dict[HVACMode, str] = {
    HVACMode.COOL: "COOL",
    HVACMode.HEAT: "HEAT",
    HVACMode.DRY: "DRY",
    HVACMode.FAN_ONLY: "FAN",
    HVACMode.HEAT_COOL: "AUTO",
}

SUPPORTED_HVAC_MODES = [
    HVACMode.OFF,
    HVACMode.COOL,
    HVACMode.HEAT,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.HEAT_COOL,
]

MIN_TEMP = 16.0
MAX_TEMP = 31.0
TEMP_STEP = 0.5
