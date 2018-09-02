#!/usr/bin/python

# ============================================================================
# File: monitor.py
# ------------------------------
#
# Clean room monitor based on rpi with dht22, bmp186 and dc17000.
#
# Notes:
#   -
#
# Layout:
#   configure and prepare
#
# Status:
#   in progress
#
# Author: Florian Pitters
#
# ============================================================================

import time, os, sys
import devices
#import Adafruit_DHT as dht
#import Adafruit_BMP as bmp



class clean_room_monitor(object):
    """ Log humidty, temperature, pressure and particle count. """

    def initialise(self):

        self.hum_meter_pin = 24         # gpio pin of humidity monitor
        self.mano_meter_pin = 17        # gpio pin of pressure monitor
        self.counter_address = 'COM3'   # serial port particle counter

        self.wait = 10                 # delay between measurements in [s]


    def execute(self):
        fContinous = 1

        try:
            while fContinous:
                ## Set up devices
                # dc1700 = dc1700(self.counter_address)
                # dht22 = dht.DHT22
                # bmp186 = bmp.BMP085.BMP085()

                ## Prepare
                hd = '# Date | Time | Temperature [C] | Humidity [%]| | Pressure [Bar] | Particles > 0.5 um [m^-3] | Particles > 2.5 um [m^-3] | ISO | Class\n'

                ## Read measurements
                date = time.strftime("%Y/%m/%d", time.localtime())
                clock = time.strftime("%H:%M:%S", time.localtime())
                #hum, temp = dht.read_retry(22, self.hum_meter_pin)
                #pres = bmp186.read_pressure()
                #cnt05, cnt25 = dc1700.read()

                hum = temp = pres = cnt05 = cnt25 = -1

                time.sleep(0.001)

                ## Determine cleanroom class from particle count
                if (cnt05 < 352000 and cnt25 < 11720):
                    iso = 7
                    clas = 10000
                elif (cnt05 < 3520000 and cnt25 < 117200):
                    iso = 8
                    clas = 100000
                else:
                    iso = 9
                    clas = 1000000

                line = [date, clock, temp, hum, pres, cnt05, cnt25, iso, clas]

                ## Print feedback
                if fPrint:
                    print '{:s}  {:s}  {:3.1f}%  {:3.1f}C  {:d}  {:d}  {:d}  {:d}  {:d}'.format(*line)

                ## One file per day
                file_name = time.strftime("%Y_%m_%d", time.localtime())

                ## Create file if it does not already exists
                if not (os.path.isfile('logs/' + file_name + '.txt')):
                    file = open('logs/' + file_name + '.txt', 'w')
                    file.write(hd)
                    file.close()

                ## Append file
                file = open('logs/' + file_name + '.txt', 'a')
                file.write('{:s}  {:s}  {:3.1f}%  {:3.1f}C  {:d}  {:d}  {:d}  {:d}  {:d}\n'.format(*line))
                file.close()

                if fSingle:
                    fContinous = 0




            ## Break if keyboard interrupt
            except KeyboardInterrupt:
                print "Keyboard interrupt." #self.logging.error("Keyboard interrupt.")



if __name__=="__main__":

    run = clean_room_monitor()
    run.initialise()
    run.execute()
