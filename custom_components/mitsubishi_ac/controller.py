"""Async client for the Mitsubishi AC controller."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import aiohttp

from .const import ENDPOINT_PATH


@dataclass
class GroupState:
    """State of a single AC group."""

    group: str
    drive: str  # ON / OFF
    mode: str  # COOL, HEAT, DRY, FAN, AUTO, ...
    set_temp: float | None
    inlet_temp: float | None


def _build_xml(command: str, inner_xml: str) -> str:
    """Build a full XML packet."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Packet><Command>{command}</Command>"
        f"<DatabaseManager>{inner_xml}</DatabaseManager></Packet>"
    )


def _build_get_mnet(group: str, attrs: list[str]) -> str:
    """Build a getRequest for Mnet attributes."""
    attr_str = " ".join(f'{a}="*"' for a in attrs)
    inner = f'<Mnet Group="{group}" {attr_str} />'
    return _build_xml("getRequest", inner)


def _build_set_mnet(group: str, attrs: dict[str, str]) -> str:
    """Build a setRequest for Mnet attributes."""
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    inner = f'<Mnet Group="{group}" {attr_str} />'
    return _build_xml("setRequest", inner)


def _parse_mnet_attrs(xml_text: str) -> dict[str, str]:
    """Parse the Mnet element attributes from a response."""
    root = ET.fromstring(xml_text)
    mnet = root.find(".//Mnet")
    if mnet is None:
        return {}
    return dict(mnet.attrib)


def _safe_float(value: str | None) -> float | None:
    """Convert a string to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class MitsubishiACController:
    """Async controller client for Mitsubishi AC."""

    def __init__(self, host: str, port: int = 80) -> None:
        """Initialize the controller."""
        self._base_url = f"http://{host}:{port}{ENDPOINT_PATH}"

    async def _post(self, session: aiohttp.ClientSession, data: str) -> str:
        """Send a POST request to the controller."""
        async with session.post(
            self._base_url,
            data=data,
            headers={"Content-Type": "text/xml"},
        ) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def async_get_group_state(
        self, session: aiohttp.ClientSession, group: str
    ) -> GroupState:
        """Get the full state of a group."""
        xml = _build_get_mnet(
            group, ["Drive", "Mode", "SetTemp", "InletTemp"]
        )
        response = await self._post(session, xml)
        attrs = _parse_mnet_attrs(response)
        return GroupState(
            group=group,
            drive=attrs.get("Drive", "OFF"),
            mode=attrs.get("Mode", "AUTO"),
            set_temp=_safe_float(attrs.get("SetTemp")),
            inlet_temp=_safe_float(attrs.get("InletTemp")),
        )

    async def async_set_drive(
        self, session: aiohttp.ClientSession, group: str, value: str
    ) -> None:
        """Set the drive (ON/OFF) for a group."""
        xml = _build_set_mnet(group, {"Drive": value})
        await self._post(session, xml)

    async def async_set_mode(
        self, session: aiohttp.ClientSession, group: str, value: str
    ) -> None:
        """Set the mode for a group."""
        xml = _build_set_mnet(group, {"Mode": value})
        await self._post(session, xml)

    async def async_set_temperature(
        self, session: aiohttp.ClientSession, group: str, value: float
    ) -> None:
        """Set the target temperature for a group."""
        xml = _build_set_mnet(group, {"SetTemp": str(value)})
        await self._post(session, xml)

    async def async_discover_groups(
        self, session: aiohttp.ClientSession
    ) -> list[str]:
        """Discover available groups via MnetList."""
        xml = _build_xml(
            "getRequest",
            "<ControlGroup><MnetList /></ControlGroup>",
        )
        response = await self._post(session, xml)
        root = ET.fromstring(response)
        groups: list[str] = []
        for mnet in root.iter("Mnet"):
            group = mnet.get("Group")
            if group is not None:
                groups.append(group)
        return groups
