# Mitsubishi AC — Home Assistant Integration

Custom integration for Home Assistant that controls Mitsubishi AC units via the centralized HTTP/XML controller (e.g. AG-150A, AE-200A).

## Features

- Auto-discovers all AC groups from the controller
- Climate entity per group with current temperature, target temperature, and HVAC mode
- Supports: on/off, set temperature, set mode (Cool, Heat, Dry, Fan, Auto)
- Polls state every 30 seconds
- Fully local — no cloud dependency

## Installation via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=fapgomes&repository=mitsubishi_ac&category=integration)

Or manually:

1. Open **HACS** → **Integrations**
2. Click the 3 dots (top right) → **Custom repositories**
3. Add `https://github.com/fapgomes/mitsubishi_ac` with type **Integration**
4. Search for **Mitsubishi AC** → **Download**
5. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **+ Add Integration**
2. Search for **Mitsubishi AC**
3. Enter the IP address of your controller
4. AC groups are discovered automatically and appear as `climate` entities

## Supported Modes

| Home Assistant | Controller |
|----------------|------------|
| Cool           | COOL       |
| Heat           | HEAT       |
| Dry            | DRY        |
| Fan only       | FAN        |
| Heat/Cool      | AUTO       |
