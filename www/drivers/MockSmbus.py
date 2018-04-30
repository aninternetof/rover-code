"""A dummy class for mocking out smbus when not running on target hardware."""
from random import randint


class MockSmbus():
    """A dummy to mock out an smbus."""

    def write_byte_data(self, *args, **kwargs):
        """Do nothing."""
        print "Writing byte data with args {} {}"\
            .format(str(args), str(kwargs))

    def read_i2c_block_data(self, addr, reg, how_many):
        """Return as many random bytes as requested."""
        return [randint(0, 255)] * how_many
