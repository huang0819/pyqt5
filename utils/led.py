import RPi.GPIO as GPIO
import logging


class LedController:
    def __init__(self, channel_r=13, channel_b=19, channel_g=26):
        self.channel_r = channel_r  # board 33 -> bcm 13
        self.channel_b = channel_b  # board 35 -> bcm 19
        self.channel_g = channel_g  # board 37 -> bcm 26

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel_r, GPIO.OUT)
        GPIO.setup(self.channel_b, GPIO.OUT)
        GPIO.setup(self.channel_g, GPIO.OUT)

        logging.info('[LED] setup module')

    def set_value(self, value_r, value_g, value_b):
        GPIO.output(self.channel_r, value_r)
        GPIO.output(self.channel_b, value_b)
        GPIO.output(self.channel_g, value_g)

    def clear_GPIO(self):
        GPIO.cleanup()
