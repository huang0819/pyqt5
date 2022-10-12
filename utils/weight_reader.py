import logging
import RPi.GPIO as GPIO

from utils.hx711 import HX711


class WeightReader:
    val = 0

    def __init__(self, dout=5, pd_sck=6, reference_unit=1):
        self.hx = HX711(dout, pd_sck)
        self.hx.set_reading_format('MSB', 'MSB')
        self.reference_unit = reference_unit

    def setup(self):
        self.val = 0
        self.hx.set_reference_unit(self.reference_unit)
        self.hx.reset()
        self.hx.tare(50)

        logging.info('[WEIGHT] setup module')

    def cleanAndExit(self):
        GPIO.cleanup()

    def read(self, debug=False):
        if debug:
            self.val = self.hx.get_weight(5)
        else:
            self.val = max(0, self.hx.get_weight(5))
        self.hx.power_down()
        self.hx.power_up()

    def reset(self):
        self.hx.reset()
        self.hx.set_offset(0)
        self.hx.set_reference_unit(1)
