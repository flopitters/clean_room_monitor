import time
import serial

class dc1700(object):
    """
    Dylos DC1700 dust counter.

    Example:
    -------------
    dev = dc1700(port='/dev/ttyUSB0')
    print dev.read_particle_counts()
    """

    def __init__(self, port='/dev/ttyUSB0'):

        self.termination = '\r\n'

        ## Set up control
        self.ctrl = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            # write_timeout=1,
            # timeout=0.001,
        )

    def query(self, cmd, debug=0):
        out = ''
        time.sleep(1)
        self.ctrl.write(cmd + self.termination)
        time.sleep(60)
        while self.ctrl.inWaiting() > 0:
            out += self.ctrl.read(1)
            if debug:
                print ">> " + out
        return out
        
    def read_particle_counts(self, debug=0):
        ret = self.query("D", debug=0)
        ret = ret.split(',')

        if debug:
            print ret

        val1 = -1
        val2 = -1

        try:
            if len(ret) == 2:
                val1 = float(ret[-2])
                val2 = float(ret[-1])
            elif len(ret) == 3:
                val1 = float(ret[-3])
                val2 = float(ret[-1])
            elif len(ret) > 3:
                val1 = float(ret[-2])
                val2 = float(ret[-1])
        except ValueError:
            pass
        
        return val1, val2
