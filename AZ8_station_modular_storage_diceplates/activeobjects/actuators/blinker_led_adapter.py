class AdapterOutput(object):
    def __init__(self, hw_output):
        self._value = 0
        self._shutter_is_open = True
        self._hw_output = hw_output

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        if self._shutter_is_open:
            self._hw_output.value = self._value
        else:
            self._hw_output.value = 0


class BlinkerLedAdapter(object):
    """ This class adapts LED and Blinker and makes a blinking LED """

    def __init__(self, hw_output_red, hw_output_green, hw_output_blue):
        self._shutter_is_open = True

        self.hw_output_red = hw_output_red
        self.hw_output_green = hw_output_green
        self.hw_output_blue = hw_output_blue

        self.red = AdapterOutput(self.hw_output_red)
        self.green = AdapterOutput(self.hw_output_green)
        self.blue = AdapterOutput(self.hw_output_blue)



    def shutter_open(self):
        self.red._shutter_is_open = True
        self.blue._shutter_is_open = True
        self.green._shutter_is_open = True

        self.hw_output_red.value = self.red.value
        self.hw_output_green.value = self.green.value
        self.hw_output_blue.value = self.blue.value

    def shutter_close(self):
        self.red._shutter_is_open = False
        self.blue._shutter_is_open = False
        self.green._shutter_is_open = False

        self.hw_output_red.value = 0
        self.hw_output_green.value = 0
        self.hw_output_blue.value = 0
