''' Helper modole for the VCNL4010 IR distance and ambient light sensor
    Adapted from https://www.controleverything.com/content/Light?sku=VCNL4010_I2CS#tabs-0-product_tabset-2
'''

import smbus

from MockSmbus import MockSmbus


class VCNL4010:

    def __init__(self, i2c_port, i2c_addr, led_current=None, binary_threshold=None):

        if not (led_current and binary_threshold):
            led_current = 0x0A
            binary_threshold = 2150
        self.binary_threshold = binary_threshold

        print "Setting up VCNL4010 with LED current {} and threshold {}".format(led_current, self.binary_threshold)

        try:
            self.bus = smbus.SMBus(i2c_port)
        except IOError as e:
            print "VCNL4010 was unable to connect to I2C bus {}. Mocking out the bus".format(i2c_port)
            self.bus = MockSmbus()

        self.i2c_addr = i2c_addr
        
        # command register, 0x80
        # 0xFF(255) Enable ALS and proximity measurement, LP oscillator
        self.bus.write_byte_data(i2c_addr, 0x80, 0xFF)

        # proximity rate register, 0x82
        # 0x00(00) 1.95 proximity measeurements/sec
        self.bus.write_byte_data(i2c_addr, 0x82, 0x00)

        # LED current register, 0x83
        # variable led_current*10 mA
        self.bus.write_byte_data(i2c_addr, 0x83, led_current)

        # ambient light register, 0x84(132)^M
        # 0x9D Continuos conversion mode, ALS rate 2 samples/sec
        self.bus.write_byte_data(i2c_addr, 0x84, 0x9D)

    def get_values(self):
        # Read data back from 0x85, 4 bytes
        # luminance MSB, luminance LSB, Proximity MSB, Proximity LSB
        data = self.bus.read_i2c_block_data(self.i2c_addr, 0x85, 4)

        # Convert the data
        luminance = data[0] * 256 + data[1]  # lux
        proximity = data[2] * 256 + data[3]  # some meaningless unit, bigger means closer
        return proximity, luminance

    def is_high(self):
        prox, lux = self.get_values()
        # to match the old GPIO sensors, we'll make this sensor active low, so a binary LOW output means object detected
        # larger integer means object is closer
        # so a smaller integer means no object detected and a binary HIGH output. 
        return prox < self.binary_threshold