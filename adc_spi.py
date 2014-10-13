import spidev
import time

class ADC_SPI:
    """
        Base ADC Class for the RPI.
    """
    # Initialize
    def __init__(self, name = "ADC", spi_channel = 1, spi_rate = 100000,\
        adc_reg_len = 8, adc_level = 5.0, adc_res_bits = 8,\
        spi_mode = 0, spi_lsb = False):
        self._spi = spidev.SpiDev()
        self._spi.open(0, spi_channel)
        self._spi.mode = spi_mode
        self._spi.max_speed_hz = spi_rate
        self._spi.lsbfirst = spi_lsb
        self._level = adc_level
        self._reg_len =  adc_reg_len
        self._res = adc_res_bits
        self._control_bits = ""
        for dummy_index in range(adc_reg_len):
            self._control_bits += "1"
        self._value_reg = []
        self._value_addr = ""

    # Show Variables
    def level(self):
        return self._level

    def reg_len(self):
        return self._reg_len

    def res(self):
        return self._res

    def spi_mode(self):
        return self._spi.mode

    def spi_rate(self):
        return self._spi.max_speed_hz

    def control_bits(self):
        return self._control_bits

    def value_reg(self):
        return self._value_reg

    def value_addr(self):
        return self._value_addr
    
    def lsb_first(self):
        return self._spi.lsbfirst

    # Helper Functions
    def __bits_to_hex(self, bits):
        return hex(int(bits, 2))

    def __hex_to_dec(self, hexa):
        return int(hexa, 0)

    def __int_to_bits(self, integer):
        return bin(integer).split("b")[-1]

    def reverse_bits(self, bits):
        bits = ((bits & 0xF0) >> 4) | ((bits & 0x0F) << 4)
        bits = ((bits & 0xCC) >> 2) | ((bits & 0x33) << 2)
        bits = ((bits & 0xAA) >> 1) | ((bits & 0x55) << 1)

    def value(self, data_position = 0):
        """
            Gets the value from a string of bits.
            The data_position is where the data actually is in
            the value_reg. Data order is DataN...Data0. 
        """
        if len(self._value_reg) <= 0:
            return
        self._value_addr = self._value_reg[0][:data_position]
        value_bits = ""
        for data_index in range(len(self._value_reg)):
            if data_index == 0:
                value_bits += self._value_reg[data_index][data_position:]
            else:
                value_bits += self._value_reg[data_index]
        value_bits = value_bits[data_position:]
        print value_bits
        print data_position
        value = int(hex(int(value_bits, 2)), 0)
        adc_res = ""
        for dummy_index in range(self._res):
            adc_res += "1"
        adc_res = int(hex(int(adc_res, 2)), 0)
        level = (self._level / float(adc_res)) * float(value)
        return level

    def send_data(self, position = 0, cs_active = 0):
        """
            Send the control bits through MOSI and gets a list of 
            bits from the MISO. The control bits are based on the 
            registers of the ADC. Zeros pad the start or the end
            depending on the position setting.
            
            Given:
                Nothing, position, and/or cs_active
            Note:
                cs_active determines if CS is active or low during 
                data transitions.
            EX (for position):
            self._control_bits = "100001000"
            position = 0
            MOSI <- (x_out =  "00000001")
            MISO <- (x_ret)
            MOSI <- (x_out = "00001000")
            MISO <- (x_ret)
            self._value_reg <- ["00000001", "00001000"]
        """
        reg_data = []
        control_bits = self._control_bits
        if len(control_bits) > 8:
            if position == 0:
                while len(control_bits) > 8:
                    reg_data.insert(0, control_bits[-8:])
                    control_bits = control_bits[:-8]
                while len(control_bits) < 8:
                    control_bits = "0" + control_bits
                reg_data.insert(0, control_bits)
            else:
                while len(control_bits) > 8:
                    reg_data.append(control_bits[:8])
                    control_bits = control_bits[8:]
                while len(control_bits) < 8:
                    control_bits += "0"
                reg_data.append(control_bits)
        else:
            reg_data.append(control_bits)
        print reg_data
        self._value_reg = []
        return_value = None
        for data in reg_data:
            if cs_active == 0:
                return_value = self._spi.xfer([int(self.__bits_to_hex(data), 0)])
                print return_value
            else:
                return_value = self._spi.xfer2([int(self.__bits_to_hex(data), 0)])
            return_value = self.__int_to_bits(return_value[0])
            self._value_reg.append(return_value)
        print self._value_reg
        
    def change_name(self, adc_name):
        self._name = adc_name

    def set_lsb(self, lsb):
        self._spi.lsbfirst = lsb

    def set_level(self, adc_level):
        self._level = adc_level

    def set_res(self, adc_res):
        self._res = adc_res

    def set_rate(self, rate):
        self._spi.max_speed_hz = rate

    def set_mode(self, mode):
        """
            Set the spi mode based on the decimal value 0 to 3.
            The decimal value is relative to the binary table 00 to 11.
            The binary order is CPOL|CPHA.
            CPOL: 0 represents the data captured on the rising edge.
                  1 represents the data captured on the falling edge.
            CPHA: 0 represents the data captured on the CPOL edge and the 
                    data propogated on the opposite CPOL edge.
                  1 represents the data captured on the opposite CPOL edge
                    and the data propogated on the CPOL edge. 
        """
        self._spi.mode = mode

    def set_control_bits(self, control_bits, position = 0):
        if len(control_bits) % 8 == 0:
            self._control_bits = control_bits
        else:
            length = len(control_bits)
            remainder = len(control_bits) % 8
            if position == 0:
                temp_control_bits = control_bits[:length]
                while len(temp_control_bits) < 8:
                    temp_control_bits = "0" + temp_control_bits
                self._control_bits = temp_control_bits + control_bits[length:]
            else:
                while len(control_bits) % 8 != 0:
                    control_bits += "0"
                self._control_bits = control_bits

