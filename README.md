# Rotary Controller Python

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

## Configuration of the servo axis parameters

The servo axis can be configured to operate in one of two possible modes:
 - Rotary Table
 - Electronic Lead Screw

When the servo is configured to operate in rotary table mode, the position is reported back in degrees, therefore
the configuration of the numerator and denominator for the input encoder shall be configured to reflect a full 
rotation of the controlled device.

When the servo is configured to operate in ELS mode, the position reported back is a relative offset of the leadscrew
travel.

Internally the system always operates in metric, regardless of the mode selected by the user, so all the ratios
and settings in the setup page have to reflect 

parameters:
- lead screw pitch configuration in mm (how many steps does it take to advance for the specified pitch)
- encoder input for the spindle, we know how many steps for a full rotation

the user configures the feed amount per revolution, the system calculates the ratio for the output axis so that
one full revolution of the spindle moves the output axis by the required amount:

lead screw pitch configuration as in how many steps to move a given amount, for example:
4TPI lead screw:
4 TPI means 4 threads per inch, so the pitch is 0.25" -> 1/4

Since we operate in metric, this number has to be converted to metric:
1/4 * 10/254

Let's look at the final ratio that needs to be configured in order to get the required feed:

Example:
encoder: 4096 pulses per revolution

lead screw: 4TPI

required feed: 0.003" per revolution

lead_screw_pulses = spindle_pulses * spindle_ratio * lead_screw_pitch * pulses_per_pitch * requested_feed
