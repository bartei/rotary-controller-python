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

## Communication protocol

The rotary controller software running on the Raspberry PI is connected
to the peripheral interface board using MODBUS RTU carried by RS485.

There is another project for the generation of a suitable raspberry
operating system image which already has all the proper settings configured
to enable the embedded UART controller for use as the communication channel
for this application.

### TODO: Provide links
The rotary controller is tested using a dedicated power supply and communication
board which is also available in another project if you wanna build it yourself.


## Device address and communication settings

The daughter board has fixed communication settings configured from the embedded
software, there are no user accessible ways to change the configuration. 

It is possible to change the communication settings if needed by modifying the 
configuration file for the firmware and by uploading the updated software to the 
daughter board.

The current settings are the following:
- Modbus RTU slave node address: 17
- Bitrate: 115200
- Party: N
- Stop Bits: 1

## Modbus Registers

The status and control of the daugther board is achieved by reading/writing Modbus 
registers. 

There are some limitations to the maximum number of registers that can be transferred
in a single operation. The current Python UI doesn't require large amounts of data to be
transferred in a single operation, but such limitations shall be taken into account if 
shall the user decided to implement a different control software, or use a PLC device
to communicate with the daughter board.

A summary of such registers is provided here with the associated data type.

### 00: ramps_mode_t mode; // 0
Defines the current operation mode for the device

### 02: int32_t currentPosition; // 2
### int32_t finalPosition; // 4
### int16_t unused_6;
### int32_t unused_8;
### uint16_t encoderPresetIndex;
### int32_t encoderPresetValue;
### int32_t unused_14;
### float maxSpeed;
### float minSpeed;
### float currentSpeed;
### float acceleration;
### int32_t stepRatioNum;
### int32_t stepRatioDen;
### float unused_28;
### int32_t synRatioNum;
### int32_t synRatioDen;
### int32_t synOffset;
### uint16_t synScaleIndex;
### int32_t scalesPosition[SCALES_COUNT];

```
