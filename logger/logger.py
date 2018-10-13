#!/usr/bin/python

# ============================================================================
# File: logger.py
# ------------------------------
#
# Clean room monitor based on rpi with dht22, bmp186 and dc17000.
#
# Notes:
#   - Dylos DC1700 takes 60 second to integrate
#
# Status:
#   works well
#
# Author: Florian Pitters
#
# ============================================================================

import time, os, sys
from optparse import OptionParser

import dc1700 as dc
import Adafruit_DHT as dht22
import Adafruit_BMP.BMP085 as bmp085


class clean_room_monitor(object):
    """ Log humidty, temperature, pressure and particle count. """

    def __init__(self, dat_path):

        self.dat_path = dat_path                # data path

        self.hum_meter_pin = 4                  # gpio pin of humidity monitor
        self.mano_meter_pin = 7                 # gpio pin of pressure monitor
        self.counter_address = '/dev/ttyUSB0'   # serial port particle counter

        self.use_dht22 = 1                      # flag if dht is connected
        self.use_bmp180 = 1                     # flag if bmp is connected
        self.use_dc1700 = 1                     # flag if dylos is connected

        self.wait = 10                          # time between measurements
                                                # keep in mind that the pc measurement takes 60s


    def execute(self):
        fContinous = 1
        fSingle = 1
        fPrint = 1

        try:
            while fContinous:
                ## Set up devices
                if self.use_dc1700:
                    dc1700 = dc.dc1700(self.counter_address)
                if self.use_bmp180:
                    bmp180 = bmp085.BMP085()

                ## Prepare
                hd = '# Date | Time | Temperature [C] | Humidity [%]| | Pressure [Bar] | Particles > 0.5 um [m^-3] | Particles > 2.5 um [m^-3] | ISO | Class\n'

                ## Read measurements
                date = time.strftime("%Y-%m-%d", time.localtime())
                clock = time.strftime("%H:%M:%S", time.localtime())

                hum = temp = pres = cnt05 = cnt25 = -1

                if self.use_dht22:
		            hum, temp = dht22.read_retry(22, self.hum_meter_pin)
                if self.use_bmp180:
                    pres = bmp180.read_pressure()
                if self.use_dc1700:
                    cnt05, cnt25 = dc1700.read_particle_counts() # takes 60s of integration time

                ## Determine cleanroom class from particle count per cubic inch
                if (cnt05/0.0254**3 < 352000 and cnt25/0.0254**3 < 11720):
                    iso = 7
                    clas = 10000
                elif (cnt05/0.0254**3 < 3520000 and cnt25/0.0254**3 < 117200):
                    iso = 8
                    clas = 100000
                else:
                    iso = 9
                    clas = 1000000

                line = [date, clock, temp, hum, pres, cnt05, cnt25, iso, clas]

                ## Print feedback
                if fPrint:
                    print '{:s}  {:s}  {:3.1f}  {:3.1f}  {:d}  {:.0f}  {:.0f}  {:d}  {:d}'.format(*line)

                ## One file per day
                file_name = time.strftime("%Y_%m_%d", time.localtime())

                ## Create log folder if it dpes not already exist
                if not (os.path.isdir(self.dat_path)):
                    os.makedirs(self.dat_path)

                ## Create file if it does not already exists
                if not (os.path.isfile(self.dat_path + '/' + file_name + '.txt')):
                    file = open(self.dat_path + '/' + file_name + '.txt', 'w')
                    file.write(hd)
                    file.close()

                ## Append file
                file = open(self.dat_path + '/' + file_name + '.txt', 'a')
                file.write('{:s}  {:s}  {:3.1f}  {:3.1f}  {:d}  {:.0f}  {:.0f}  {:d}  {:d}\n'.format(*line))
                file.close()

                if fSingle:
                    fContinous = 0
                else:
                    time.sleep(self.wait)


        ## Break if keyboard interrupt
        except KeyboardInterrupt:
            print "Keyboard interrupt." #self.logging.error("Keyboard interrupt.")




# Main app
# -------------------------------------

def main():
    usage = "usage: ./logger.py -d [data_path]"

    parser = OptionParser(usage=usage, version="prog 0.01")
    parser.add_option("-d", "--dat_path", action="store", dest="dat_path", type="string", default="logs/",  help="data path")

    (options, args) = parser.parse_args()
    if not (options.dat_path):
	       parser.error("You need to give a data path. Try '-h' for more info.")

    run = clean_room_monitor(options.dat_path)
    run.execute()

if __name__=="__main__":
	main()
