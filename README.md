# Rotary Controller Python (RCP)

[![Discord](https://img.shields.io/discord/1386014070632878100?style=social)](https://discord.gg/EDtgj7Yayr) [![Shop at Provvedo](https://img.shields.io/badge/Shop-Provvedo-blue?logo=shopify&style=flat-square)](https://www.provvedo.com/shop)

A **Kivy-based Digital Read-Out (DRO) and single-axis controller UI** for rotary tables and similar devices, designed to run on Raspberry Pi or desktop environments (Windows, macOS, Linux). Interfaces via RS-485 with a dedicated STM32-based control board.

🛒 **Purchase all boards from our shop:** [Provvedo Shop](https://www.provvedo.com/shop)

---

## 🚀 Features

* Responsive touch-capable UI built with **Kivy**
* Communicates over **RS-485** with an STM32 controller for stepper/encoder control ([github.com][1])
* Works on Raspberry Pi 3/4, Windows, macOS, and Linux
* Runs headless on Pi using the custom **OSPI** OS with pre-installed RCP ([github.com][1])

---

## 🎯 Requirements

* **Hardware**

  * Rotary controller board (STM32 firmware from `bartei/rotary-controller-f4`)
  * RS-485 interface (e.g. via Power Hat)
  * Raspberry Pi 3/4 for Pi deployments

* **Software**

  * Python 3.8+
  * `uv` virtual environment manager
  * `kivy`, `pyserial`, and other dependencies from `pyproject.toml`

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

For Windows, follow instructions on the \[Astral uv docs].

### 3. Create & Sync Virtual Environment

```bash
uv venv       # creates .venv/
uv sync       # installs required dependencies
```

### 4. Run the App

```bash
uv run python ./rcp/main.py
```

---

## 💻 Platform-specific Notes

### Windows/macOS/Linux

* Use Python >=3.8
* Virtual environment recommended via `uv`
* Ensure `pyserial` can access your RS-485 adapter (permissions on Linux/macOS)

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

## 🛠️ Troubleshooting

* **Serial issues**: Verify RS-485 wiring, correct serial port, and permissions
* **Service failures (Pi)**: Check `journalctl` logs and Kivy log files, check the /var/log folder for OSPI release

---

## 📚 References & Related Projects

* **Firmware & hardware:** \[rotary-controller-f4] ([github.com][3])
* **PCB design & BOM:** \[rotary-controller-pcb] ([github.com][4])
* **OSPI OS with pre-installed RCP:** \[ospi] ([github.com][2])

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

Join our Discord community for support, collaboration, and updates.

---

## 📄 License

Licensed under MIT. See `LICENSE` for full terms.

---

*README last updated: June 23, 2025*

---

[1]: https://github.com/bartei/rotary-controller-python"
[2]: https://github.com/bartei/ospi"
[3]: https://github.com/bartei/rotary-controller-f4"
[4]: https://github.com/bartei/rotary-controller-pcb"

