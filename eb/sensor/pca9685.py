"""
    Author: Ege Bilecen
    Date  : 31.01.2022

    Datasheet:
    https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
"""
from eb.i2c import I2C
from time   import sleep

class PCA9685:
    MAX_PWM_VALUE = (2 ** 12) - 1

    class REGISTER:
        MODE_1       = 0x00
        PRESCALER    = 0xFE
        FIRST_LED_ON = 0x06

    def __init__(self, 
                 addr            : int = 0x40,
                 ref_clock_speed : int = 25000000) -> None:
        self._addr = addr
        self._ref_clock_speed = ref_clock_speed
        self._bus  = I2C(addr)

    def _get_ledn_register_start_addr(self, 
                                      channel : int) -> int:
        return PCA9685.REGISTER.FIRST_LED_ON + (channel * 4)

    def get_frequency(self) -> int:
        prescale_val = self._bus.read_block_data(PCA9685.REGISTER.PRESCALER, 1)[0]

        return self._ref_clock_speed / 4096 / prescale_val

    def set_frequency(self, 
                      hz : int) -> None:
        if hz < 24 or hz > 1526:
            raise ValueError("hz must be between 24 and 1526. (Inclusive)")

        prescale_val = int(self._ref_clock_speed / (4096 * hz))
        old_mode     = self._bus.read_block_data(PCA9685.REGISTER.MODE_1, 1)[0]

        self._bus.write_byte(PCA9685.REGISTER.MODE_1, (old_mode & 0x7F) | (1 << 4)) # activate sleep
        self._bus.write_byte(PCA9685.REGISTER.PRESCALER, prescale_val)
        self._bus.write_byte(PCA9685.REGISTER.MODE_1, old_mode)
        sleep(0.005)
        self._bus.write_byte(PCA9685.REGISTER.MODE_1, old_mode | 0xA0) # Mode 1, autoincrement on, fix to stop pca9685 from accepting commands at all addresses

    def set_duty_cycle_value(self,
                             channel : int,
                             val     : int) -> None:
        if channel < 0 or channel > 15:
            raise ValueError("channel must be between 0 and 15. (Inclusive)")

        if val < 0 or val > PCA9685.MAX_PWM_VALUE:
            raise ValueError("val must be between 0 and {}. (Inclusive)".format(str(PCA9685.MAX_PWM_VALUE)))

        REGISTER_LEDn_ON_L  = self._get_ledn_register_start_addr(channel)
        REGISTER_LEDn_ON_H  = REGISTER_LEDn_ON_L  + 0x01
        REGISTER_LEDn_OFF_L = REGISTER_LEDn_ON_H  + 0x01
        REGISTER_LEDn_OFF_H = REGISTER_LEDn_OFF_L + 0x01

        if val == PCA9685.MAX_PWM_VALUE:
            self._bus.write_byte(REGISTER_LEDn_ON_L,  0x00)
            self._bus.write_byte(REGISTER_LEDn_ON_H, (1 << 4))
            self._bus.write_byte(REGISTER_LEDn_OFF_L, 0x00)
            self._bus.write_byte(REGISTER_LEDn_OFF_H, 0x00)
        else:
            off_val = val

            self._bus.write_byte(REGISTER_LEDn_ON_L,  0x00)
            self._bus.write_byte(REGISTER_LEDn_ON_H,  0x00)
            self._bus.write_byte(REGISTER_LEDn_OFF_L, off_val & 0x00FF)
            self._bus.write_byte(REGISTER_LEDn_OFF_H, off_val & 0xFF00)

    def set_duty_cycle_percentage(self,
                                  channel    : int,
                                  percentage : int) -> None:
        if percentage < 0 or percentage > 100:
            raise ValueError("percentage must be between 0 and 100. (Inclusive)")

        self.set_duty_cycle_value(channel, int(PCA9685.MAX_PWM_VALUE * percentage / 100))

    def get_dutcy_cycle_value(self,
                              channel : int) -> int:
        if channel < 0 or channel > 15:
            raise ValueError("channel must be between 0 and 15. (Inclusive)")
        
        block_data = self._bus.read_block_data(self._get_ledn_register_start_addr(channel), 4)

        if block_data[1] & (1 << 4) == 0x01:
            return PCA9685.MAX_PWM_VALUE

        return PCA9685.MAX_PWM_VALUE - ((block_data[3] << 8) | block_data[2])

    def get_duty_cycle_percentage(self,
                                  channel : int) -> int:
        return int(self.get_dutcy_cycle_value(channel) / self.MAX_PWM_VALUE * 100)
