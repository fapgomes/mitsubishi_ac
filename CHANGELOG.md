# Changelog

## 1.0.1 — 2026-02-26

- Fix group discovery: parse MnetRecord elements instead of Mnet
- Use GroupNameWeb from controller as entity names (e.g. "RECEÇAO", "LOUNGE")

## 1.0.0 — 2026-02-26

- Initial release
- Home Assistant custom integration with config flow UI
- Async controller client (aiohttp) for Mitsubishi AC HTTP/XML protocol
- Auto-discovery of AC groups via MnetList
- Climate entities with on/off, temperature, and HVAC mode control
- DataUpdateCoordinator polling every 30 seconds
- HACS support
