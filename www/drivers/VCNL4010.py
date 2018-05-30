"""
Helper modole for the VCNL4010 IR distance and ambient light sensor.

Adapted from:
https://www.controleverything.com/content/Light?sku=VCNL4010_I2CS#tabs-0-product_tabset-2
"""

try:
    import smbus
except ImportError:
    pass

from MockSmbus import MockSmbus


class VCNL4010:
    """A module to set up and read from a VCNL4010."""

    def __init__(self, i2c_port, i2c_addr,
                 led_current=None, binary_threshold=None):
        """Create a VCNL4010 driver module."""
        if not (led_current and binary_threshold):
            led_current = 0x0A
            binary_threshold = 2150
        self.binary_threshold = binary_threshold

        print "Setting up VCNL4010 with LED current {} and threshold {}"\
            .format(led_current, self.binary_threshold)

        try:
            self.bus = smbus.SMBus(i2c_port)
        except (IOError, NameError):
            print "VCNL4010 was unable to connect to I2C bus {}. " \
                  "Mocking out the bus".format(i2c_port)
            self.bus = MockSmbus()

        self.i2c_addr = i2c_addr

        try:
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
        except IOError:
            print 'Failed to init VCNL4010 at port {}, address {}'\
                .format(i2c_port, i2c_addr)

    def get_values(self):
        """Return the proximity and luminance."""
        # Read data back from 0x85, 4 bytes
        # luminance MSB, luminance LSB, Proximity MSB, Proximity LSB
        try:
            data = self.bus.read_i2c_block_data(self.i2c_addr, 0x85, 4)
        except IOError:
            print 'Failed to read VCNL4010 at address {} register 0x85'\
                .format(self.i2c_addr)
            raise

        # Convert the data
        luminance = data[0] * 256 + data[1]  # lux
        proximity = data[2] * 256 + data[3]  # bigger means closer
        return proximity, luminance

    def is_high(self):
        """HIGH, meaning "not seeing something"."""
        prox, lux = self.get_values()
        # to match the old GPIO sensors, we'll make this sensor active low
        # a binary LOW output means object detected
        # larger integer means object is closer
        # a smaller integer means no object detected and a binary HIGH output.
        return prox < self.binary_threshold
