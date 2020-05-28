# soft-manip-rs
High-level controller for soft robotic manipulator. Sensors and Embedded Systems for IoT project.

This repository contains firmware for microcontrollers and web application for Raspberry Pi 4 (Pi camera is needed) 

## Running application server
Firstly, you should install necessary libraries.
To install libraries, you can use pip installer (for Python3)
* Flask
* opencv-python
* numpy
* picamera
* imutils
* matplotlib
```bash
    pip3 install <library_name>
```

### Variant 1:
At the second stage you must specify running parameters and setup Flask system variable:
```bash
    cd Application/
    export FLASK_APP=app.py
```

To run application bash command is used:
```bash
    flask run --host=0.0.0.0
```

### Variant	2
To run application bash command is used:
```bash
	cd Application/
    python3 app.py
```
