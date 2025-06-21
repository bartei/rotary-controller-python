# Rotary Controller Python

![Discord](https://img.shields.io/discord/1386014070632878100?style=social&link=https%3A%2F%2Fdiscord.gg%2F69Qr5PSu)


This project is a Kivy based user interface developed for the Raspberry PI for the control of rotary tables and
similar devices on manual milling machines, tool grinders and similar equipment.

This software is designed to operate with an RS485 connected control board which is responsible for the precise
timing required to control stepper motors as well as the acquisition of high speed encoder signals.

Links for the hardware and firmware needed to complete the project are provided below.

This software is tested on Raspberry PI 4 and 3B and it is recommended to run it from the console using the 
configuration and libraries suggested by the Kivy project maintainers.

When running this kivy app from a desktop environment, a significant performance loss is evident.

Prebuilt images will be provided eventually so that installation friction can be minimized.

This is still currently under heavy development, further features and pluggable boards will eventually be provided
to offer further functionality to the system.

## Getting started

This software can be executed from any Python compatible operating system, it has been successfully tested on
Windows, Linux and OSX. The recommended way to setup your development environment is to use `pyenv` for the
configuration of a suitable python version in your machine and for the creation of a dedicated virtual envionment.

There are thousands of guides online for the method described above, so for now I'm not gonna write down specific
instructions about it. 

Once a compatible version of Python is installed with pyenv and a suitable virtual environment has been created, 
it will be sufficient to install the requirements found in the requirements file.

### Installing the dependencies and creating the virtual environment

This project uses uv to manage the virtual environment and the package dependencies. Here is a quick start installation
command that you can use to install uv on your development environment on Linux/Mac:
```shell
 curl -LsSf https://astral.sh/uv/install.sh | sh
 ```
For other operating systems please refer to the documentation provided by the Astral UV maintainers.

Once uv is installed and available form your command prompt place yourself into the rotary-controller-python folder,
then run the following command to create a `.venv` environment:
```shell
uv venv
```

Once the virtual environment is created and it's available you can proceed with the installation of all the 
dependencies with the following command:
```shell
uv sync
```

With the above command, all the compatible versions of the specified packages will be installed in your newly created
virtual environment.

From this point on you can proceed as with any other virtual environment for python to execute, debug and develop this
project.

Here is a list of example commands that you might need during your development:
```bash
# All the next example commands assume that you're in the rotary-controller-python folder and that the venv and
# dependencies are already installed following the previous insturctions!

# Add a new package dependency
uv add package_name

# Check for new versions available
uv sync

# Activate the virtual environment
source ./.venv/bin/activate

# Run the application without activating the environment
./.venv/bin/python ./rcp/main.py

# Run the application letting uv chose the right python
uv run python ./rcp/main.py

```

## OSPI Operating system notes

The OSPI operating system, available at the following address [OSPI Repository](https://github.com/bartei/ospi) comes
with the latest version (at build time) of RCP already preinstalled.

The installation of the RCP service on the OSPI operating system is done under the `/root` folder, under the 
rotary-controller-python folder.

If the OSPI operating system has access to internet, updating the software version of RCP from within the device is 
a simple process that can be carried out following those instructions:
```
# Connect a keyboard to the Raspberry PI device and press the ESC button to terminate the RCP service
# Go to tty1 by pressing ALT+F2
# Enter the default username and password: default/default
# Once you are the the terminal prompt enter the following command to gain root:
sudo su

# Go to the root folder
cd

# go to the rotary-controller-python project folder
cd rotary-controller-python

# Perform a git pull to get the latest version of the software
git pull

# Update all the dependencies with uv
uv sync

# Reboot
reboot
```

### Breaking changes and logs on OSPI

Occasionally there might be breaking changes in the software, in which case the major version of the RCP software would
be different form the one currently running on your devices. In the unfortunate occurrence that your RCP stops working,
there are a few useful resources that can be consulted to understand the root cause of the failure:
```shell
# The following instructions assume that you are already logged into the device as per the previous example, and that
you have already gained root privileges on the device, you should be on the root folder of the project directory:

# Check the service logs from journalctl
systemctl status rotary-controller

# Check more history on the jorunalctl
journalctl -xeu rotary-controller

# Review the kivy logs
cd /var/log
ls # --> This will show you a list of log files, look for the latest one produced by kivy and cat the contents
```


# Description of Servo Operation Modes and Configuration

When the servo is configured to operate in **rotary table mode**, the position is reported in **degrees**. Therefore, 
the configuration of the numerator and denominator for the input encoder must be set to reflect a full rotation of the 
controlled device. This ensures accurate reporting and control of the servo's position.

In contrast, when the servo is configured to operate in **ELS (Electronic Leadscrew) mode**, the position is reported 
as a **relative offset of the leadscrew travel**, rather than an absolute value.

## Internal Operation

Internally, the system always operates using **metric units**, regardless of the mode selected by the user. 
Consequently, all ratios and settings in the setup page must be configured using metric values. This consistency is 
essential for precise calculations and control.

---

## Configuration Parameters

The system requires the following parameters to be configured:

1. **Leadscrew Pitch**:
    - Specifies the pitch of the leadscrew in millimeters.
    - For example, the pitch determines how far the axis moves for a complete rotation of the leadscrew.

2. **Spindle Encoder Input**:
    - Indicates how many pulses the spindle encoder generates per full revolution.

3. **Feed Amount Per Revolution**:
    - The user configures the desired feed (movement of the axis) per spindle revolution.
    - The system calculates the output axis ratio to ensure one full spindle revolution moves the output axis by the 
      specified amount.

---

## Example: Leadscrew Pitch

For a leadscrew with a pitch of **4 TPI (Threads Per Inch)**:
- **4 TPI** means there are 4 threads per inch, resulting in a pitch of 1/4 inches, or 0.25 inches.
- Since the system operates in metric, the pitch is converted to millimeters: pitch_in_mm = 1/4 * 10/254

---

## Calculating the Final Ratio

To achieve the required feed rate, the system computes the final ratio for the leadscrew based on the following equation:

lead_screw_pulses = spindle_pulses * spindle_ratio * lead_screw_pitch * pulses_per_pitch * requested_feed

### Example:

- **Spindle Encoder**: 4096 pulses per revolution.
- **Leadscrew Pitch**: 4 TPI
- **Required Feed**: 0.003 inches per revolution

### Steps:

1. Convert the pitch to metric:
   1/4 * 10/254

2. Calculate the necessary lead screw pulses based on the formula above.
