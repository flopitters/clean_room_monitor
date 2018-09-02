from device import device, device_error


class dc1700(device):
    """
    Dylos DC1700 dust counter.

    Example:
    -------------
    dev = dc1700(port=24, baudrate=9600)
    print dev.read()
    """

    def __init__(self, port):
        device.__init__(self, port=port, baudrate=9600, parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001)

    def read(self):
        ret = self.ctrl.query("D")
        print ret.split(',')

        return float(ret)
