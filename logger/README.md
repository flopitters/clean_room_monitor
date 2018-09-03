# Clean Room Monitor

A repo for raspberry pi based monitor for a clean room. Made for a DHT22 humidity sensor, BMP180 pressure sensor and Dylas DC1700 dust monitor.

## Setup the RPi

Follow the instructions here to set up your RPi https://ubuntu-mate.org/raspberry-pi/ or https://www.raspberrypi.org/learning/software-guide/quickstart/. You can also use etcher to write the image to the sd card.

Connect a power supply, monitor, keyboard and mouse. Boot up the RPi and finish the installation. Don't forget to active ssh, i2c, gpio's and serial access from remote.
```bash
raspi-config
```
Add some useful software and remove the bloatware. 
```bash
# Update
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade

# Some useful software 
sudo apt-get install make cmake emacs git gnuplot build-essential
sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas python-gnuplot python-serial python-pyvisa python-dev

# Remove all the bloatware
sudo apt-get remove --purge wolfram* libreoffice* scratch minecraft-pi sonic-pi penguinspuzzle openjdk-8-jre oracle-java8-jdk openjdk-7-jre oracle-java7-jdk  -y

sudo apt-get autoremove
sudo apt-get autoclean
sudo apt-get update
```


## Register the RPi on the CERN network

Hook up the RPI to a monitor and keyboard. Start a terminal and type
```bash
ifconfig -a
```

Look for something that looks like wlan0 and eth0. These are the network ports. Note down the MAC address of both. It looks something like '8b:ae:27:38:4d'. Head to https://network.cern.ch to register your device with the right MAC addresses you found with the above commend. Make sure you add the wifi and the ethernet interface. Reboot the RPI (it might take a few minutes until the registration is done). Open a browser and finish the registration. You may need to reboot again. (If you know of a way to do this without the need to hook up a monitor, please let me know.) 


## Setup Humidity Monitor

Sensor: DHT22

Cabling:
- Plus Pin to +3.3V or 5V (Pin 1)
- Minus Pin to GND (Pin 6)
- Signal to GPIO Pin 4 (Pin 7)


## Setup Pressure Sensor

Sensor: BMP180

Cabling:
- VCC Pin to +5V (Pin 2)
- GND Pin to GND (Pin 6)
- SCL pin to I2C clock/GPIO2  (Pin 3)
- SDA pin to I2C data/GPIO3 (Pin 5)


Test if cabling is correct (you should see a number somewhere in the response table)
```bash
sudo i2cdetect -y 1
```

## GPIO Setup Python

Install Adafruit for GPIO drivers

```bash
git clone https://github.com/adafruit/Adafruit_Python_DHT.git adafruit_dht
cd adafruit_dht
sudo python setup.py install
```
```bash
git clone https://github.com/adafruit/Adafruit_Python_BMP adafruit_bmp
cd adafruit_bmp
sudo python setup.py install
```


## Further setup

Add user to access group for serial
```bash
sudo usermod -a -G dialout $USER
```

Add cron job
```bash

```

