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

To run the application simply invoke from your favorite terminal `python ./main.py`

When running the software from a raspberry pi a few preparatory steps shall be followed to ensure proper
operation of the touchscreen, keyboard, etc. etc.

Instructions will eventually be placed here for completeness to assist in the configuration of raspbian.

#TODO: Put here instructions for raspbian

