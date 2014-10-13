import adc_spi
import time

SEQ = {
    0:("0", "0"),
    1:("0", "0"),
    2:("1", "0"),
    3:("1", "1"),
}
PM = {
    0:("1", "1"),
    1:("0", "1"),
    2:("1", "0"),
    3:("1", "1"),
}
ADD = {
    0:("0", "0"),
    1:("0", "1"),
    2:("1", "0"),
    3:("1", "1"),
}
class AD7923(adc_spi.ADC_SPI):
    def __init__(self, adc_address = 0, adc_power = 3, adc_seq = 0,\
        adc_range = "1", coding = "1"):
        adc_spi.ADC_SPI.__init__(self, name = "AD7923", spi_channel = 0,\
        spi_rate = 500000, adc_reg_len = 12, adc_level = 3.3,\
        adc_res_bits = 8, spi_mode = 2, spi_lsb = False)
        self._pm = adc_power
        self._addr = adc_address
        self._seq = adc_seq
        self._range = adc_range
        self._coding = coding
        self._values = [None, None, None, None]
        self._running = False
        self._control_bits = "1111111111111111"
            
    def __str__(self):
        control = "Control Bits:\n\t" +\
            "MSB to LSB\n\t" +\
            "WRITE|SEQ1|NOP|NOP|ADD1|ADD0|PM1|" +\
            "PM0|SEQ0|NOP|RANGE|CODING|NOP...\n\t" +\
            self._control_bits
        return control 

    def adc_start(self):
        self.__adc_dummy()
        time.sleep(0.000001)
        self.update_control_bits("1")
        self.send_data()
        time.sleep(0.000001)
        self._running = True
    
    def adc_convert(self):
        if self._running == True:
            if self._pm  == 1:
                time.sleep(0.000001)
                self.send_data()
            elif self._pm == 2:
                time.sleep(0.000005)
            else:
                time.sleep(0.000001)
            self.send_data()
            return self.value(data_position = 4)

    def update_control_bits(self, write = "0"):
        print "current_control: ", self._control_bits
        print write
        print SEQ[self._seq][0]
        print SEQ[self._seq][1]
        print ADD[self._addr][0]
        print ADD[self._addr][1]
        print self._range
        print self._coding
        self._control_bits = (write + SEQ[self._seq][0] + "00" +
            ADD[self._addr][0] + ADD[self._addr][1] +
            PM[self._pm][0] + PM[self._pm][1] +
            SEQ[self._seq][1] + "0" +
            self._range + self._coding + "0000")
        print "new_control: ", self._control_bits

    def __adc_dummy(self):
        self.send_data()
