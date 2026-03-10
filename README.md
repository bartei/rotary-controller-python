# Rotary Controller Python (RCP)

[![Discord](https://img.shields.io/discord/1386014070632878100?style=social)](https://discord.gg/EDtgj7Yayr) [![Shop at Provvedo](https://img.shields.io/badge/Shop-Provvedo-blue?logo=shopify&style=flat-square)](https://www.provvedo.com/shop)

A **Kivy-based Digital Read-Out (DRO) and single-axis controller UI** for rotary tables and similar devices, designed to run on Raspberry Pi or desktop environments (Windows, macOS, Linux). Interfaces via RS-485/Modbus RTU with a dedicated STM32-based control board.

🛒 **Purchase all boards from our shop:** [Provvedo Shop](https://www.provvedo.com/shop)

---

## 🚀 Features

* Responsive touch-capable UI built with **Kivy**
* Communicates over **RS-485 Modbus RTU** with an STM32 controller ([rotary-controller-f4](https://github.com/bartei/rotary-controller-f4))
* **Configurable axes** — add/remove axes, assign hardware scale inputs, apply transforms (identity, scaling, weighted sum, angle cos/sin)
* **Electronic Lead Screw (ELS)** mode for synchronized threading and power feed on manual lathes
* **Sync mode** with configurable gear ratios for spindle-synchronized movement
* **Circle pattern calculator** for bolt hole patterns
* Customizable display: fonts, colors, digit formats (metric/imperial/angle)
* **Contextual help** — info button on every setting field with documentation and examples
* Works on Raspberry Pi 3/4/5, Windows, macOS, and Linux
* Runs headless on Pi using the custom **OSPI** OS with pre-installed RCP ([ospi](https://github.com/bartei/ospi))

---

## 🎯 Requirements

* **Hardware**

  * Rotary controller board (STM32 firmware from [rotary-controller-f4](https://github.com/bartei/rotary-controller-f4))
  * RS-485 interface (e.g. via Power Hat)
  * Raspberry Pi 3/4/5 for Pi deployments

* **Software**

  * Python 3.10+
  * [`uv`](https://docs.astral.sh/uv/) package manager

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/bartei/rotary-controller-python.git
cd rotary-controller-python
```

### 2. Install `uv`

Install `uv` (Linux/macOS):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows, see the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run the App

```bash
uv run python -m rcp.main
```

### 5. Run Tests

```bash
uv run pytest
```

---

## 💻 Platform-specific Notes

### Windows/macOS/Linux

* Python >= 3.10
* Virtual environment managed automatically by `uv`
* Ensure your RS-485 adapter is accessible (check serial port permissions on Linux/macOS)

### Raspberry Pi & OSPI

* Install an SD card image from the [OSPI project](https://github.com/bartei/ospi)
* RCP is pre-installed in `/root/rotary-controller-python/`
* To update:

  ```bash
  sudo systemctl stop rotary-controller
  cd /root/rotary-controller-python
  git pull
  uv sync
  reboot
  ```
* View logs:

  ```bash
  journalctl -u rotary-controller
  journalctl -xeu rotary-controller
  tail -n +1 /var/log/kivy*
  ```

---

## 📂 Project Structure

```
rcp/
├── main.py                    # Entry point (asyncio + Kivy event loop)
├── app.py                     # MainApp class
├── feeds.py                   # Feed/thread pitch configurations
├── help/                      # Contextual help documents (markdown)
├── components/                # UI layer
│   ├── home/                  # Home screen (coordbar, servobar, elsbar, statusbar)
│   ├── screens/               # Full-screen views (setup, scale, servo, formats, etc.)
│   ├── widgets/               # Reusable form widgets with help button support
│   ├── popups/                # Modal dialogs (keypad, help, feeds table, etc.)
│   ├── toolbars/              # Toolbar buttons
│   └── plot/                  # Plot/visualization
├── dispatchers/               # Event dispatchers and state management
│   ├── saving_dispatcher.py   # Auto-persisting properties to YAML
│   ├── formats.py             # Display format settings
│   ├── circle_pattern.py      # Circle pattern calculator
│   └── board.py               # Board/device event dispatcher
└── utils/                     # Hardware communication layer
    ├── communication.py       # ConnectionManager (Modbus RTU)
    ├── base_device.py         # C typedef parser and register I/O
    └── devices.py             # Device type definitions
```

---

## 🛠️ Troubleshooting

* **Serial issues**: Verify RS-485 wiring, correct serial port, and permissions
* **Service failures (Pi)**: Check `journalctl` logs and Kivy log files under `/var/log/`
* **Display issues**: Adjust font size and display format in the Formats setup screen

---

## 📚 References & Related Projects

* **Firmware & hardware:** [rotary-controller-f4](https://github.com/bartei/rotary-controller-f4)
* **PCB design & BOM:** [rotary-controller-pcb](https://github.com/bartei/rotary-controller-pcb)
* **OSPI OS with pre-installed RCP:** [ospi](https://github.com/bartei/ospi)

---

## 🧾 Changelog

See `CHANGELOG.md` for detailed history, updates, and breaking changes.

---

## 🤝 Contributing

Contributions are welcome! Please:

* Open issues for bugs or feature requests
* Submit pull requests or improvements
* Help with testing, documentation, porting new features

---

## 🏆 Support

Join our [Discord community](https://discord.gg/EDtgj7Yayr) for support, collaboration, and updates.

---

## 📄 License

Licensed under MIT. See `LICENSE` for full terms.