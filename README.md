# Urmet Camera for Home Assistant

This is a custom component for Home Assistant that integrates with Urmet-compatible IP cameras.

## 🎯 Features

- ✅ View RTSP live stream in Home Assistant
- ✅ Control Zoom In / Zoom Out via buttons (PTZ)
- ✅ Configurable host and credentials via UI

## 📦 Installation

1. Copy `hello_world/` to your `custom_components/` directory
2. Restart Home Assistant
3. Add integration via UI: Settings → Devices & Services → Add Integration → Urmet Camera

## ⚙️ Configuration

After installing the integration, you'll be prompted to enter:

- IP address of the camera
- Username
- Password

## 🔘 Services

This component adds two `button` entities to control PTZ Zoom:

- `button.camera_zoomin`
- `button.camera_zoomout`

Clicking the buttons will briefly send PTZ commands to move zoom in/out a small step.

## 🛠️ Known limitations

- Does not support full PTZ cruise or presets yet
- Stream URL is fixed and not autodetected via ONVIF
- Zoom control is simple step-triggered (no real-time holding)

## 🙋‍♂️ Feedback

Feel free to open issues or submit PRs via GitHub.

---

Tested with Urmet-compatible IP camera firmware (ONVIF + PTZ + RTSP supported).
