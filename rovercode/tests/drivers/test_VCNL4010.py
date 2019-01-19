"""Test the VCNL4010 sensor helper."""
from mock import patch, call, MagicMock
import pytest

from drivers.VCNL4010 import VCNL4010


def test_init():
    """Test the init, which configures the chip."""
    mockbus = MagicMock()
    with patch('smbus.SMBus', return_value=mockbus) as mock_smbus_module:
        driver = VCNL4010(1, 2, 3, 4)
        mock_smbus_module.assert_called_once_with(1)
        assert driver.i2c_addr == 2
        assert driver.binary_threshold == 4
        expected_calls = [
            call(2, 0x83, 3)  # set LED current
        ]
        mockbus.write_byte_data.assert_has_calls(expected_calls)


def test_get_is_high():
    """Test the binary interpretation of the proximity value."""
    mockbus = MagicMock()
    with patch('smbus.SMBus', return_value=mockbus):
        driver = VCNL4010(1, 2, 3, 258)
        # value larger than threshold means not high
        # lux MSB, lux LSB, prox MSB, prox LSB
        mockbus.read_i2c_block_data.return_value = [0, 0, 1, 3]
        assert not driver.is_high()
        # value smaller than threshold means high
        # lux MSB, lux LSB, prox MSB, prox LSB
        mockbus.read_i2c_block_data.return_value = [0, 0, 1, 1]
        assert driver.is_high()
        # value equal to threshold doesn't really concern us


def test_get_is_high_error():
    """Test the binary interpretation of the proximity value with an error."""
    mockbus = MagicMock()
    with patch('smbus.SMBus', return_value=mockbus):
        driver = VCNL4010(1, 2, 3, 258)
        mockbus.read_i2c_block_data.side_effect = IOError()
        with pytest.raises(IOError):
            driver.is_high()


def test_get_values():
    """Test getting the values from the sensor."""
    mockbus = MagicMock()
    with patch('smbus.SMBus', return_value=mockbus):
        driver = VCNL4010(1, 2, 3, 258)
        # lux MSB, lux LSB, prox MSB, prox LSB
        mockbus.read_i2c_block_data.return_value = [1, 2, 3, 4]
        prox, lux = driver.get_values()
        assert prox == 3 * 256 + 4
        assert lux == 1 * 256 + 2
