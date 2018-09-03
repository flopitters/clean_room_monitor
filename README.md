# Clean Room Monitor

A small program to monitor clean room humidty, pressure and dust levels.

The program is split in two parts:
- The logger is used to record the data. It is supposed to be run on a raspberry pi with a DHT22 humidty monitor, a BMP180 manometer and Dylos DC1700 particle counter.
- The monitor is used to plot the data. It is meant to run on an independent machine.

Refer to the individual README's for further instructions.