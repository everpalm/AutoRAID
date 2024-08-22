import RPi.GPIO as gpio
import logging
import time
import json

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PROJECT_PATH = "/home/pi/Projects/AutoRAID"

class RaspBerryPins(object):
    '''
    RaspBerry Pi Pin definition is singleton
    '''
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        # if not hasattr(cls, 'instance'):
        if cls._instance is None:
            cls.instance = super(RaspBerryPins, cls).__new__(cls)
        return cls.instance

    def __init__(self, pin_define_file, pin_define):
        self.pin_define_file = pin_define_file
        self._pin_define = pin_define
        self.power_switch = self.get_gpio()
        self._initialized = True

    def get_gpio(self):
        try:
            # print(f'self._pin_define = {self._pin_define}')
            with open(f'{PROJECT_PATH}/config/{self.pin_define_file}', 'r') as f:
                dict_pin_define = json.load(f)
                logger.debug(f'dict_pin_define = {dict_pin_define}')
                temp = dict_pin_define.get(self._pin_define)
                logger.debug(f'temp["physical_pin"] = {temp["physical_pin"]}')
                return temp["physical_pin"]
                # return dict_config_list
        except IOError:
            logger.error(f'Cannot open/read file: {self.pin_define_file}')
            raise


class OperateGPIO(object):
    RELAY_ACTIVE_TIME = 1
    HOLD_BUTTON_TIME = 5
    def __init__(self, pin_define, board_mode):
        self.switch_pin = pin_define.power_switch
        logger.debug(f'self.switch_pin = {self.switch_pin}')
        self._board_mode = board_mode
        gpio.setmode(self._board_mode)

        # Relay is active low
        gpio.setup(self.switch_pin, gpio.OUT, initial=gpio.HIGH)
        time.sleep(self.RELAY_ACTIVE_TIME)

    @property
    def board_mode(self):
        return self._board_mode

    @board_mode.setter
    def board_mode(self, value):
        '''
        Verbatim
            Board: 10
            BCM: 11
        '''
        if self._board_mode != value:
            gpio.setmode(value)
            self._board_mode = gpio.getmode()

    def _set_switch_mode(self):
        mode = gpio.getmode()
        logger.debug(f'self.switch_pin = {self.switch_pin}')
        logger.debug(f'mode = {mode}')
        if mode != gpio.BOARD:
            self.switch_handler()

        #Persist relay for a period of time, not a glitch
        time.sleep(self.RELAY_ACTIVE_TIME)
    
    def switch_handler(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.switch_pin, gpio.OUT)

    def hold_power_button(self):
        self._set_switch_mode()
        gpio.output(self.switch_pin, gpio.LOW)

        #Hold power button for at least 4 seconds
        time.sleep(self.HOLD_BUTTON_TIME)
    
    def press_power_button(self):
        self._set_switch_mode()        
        gpio.output(self.switch_pin, gpio.LOW)

        #Persist relay for a period of time, not a glitch
        time.sleep(self.RELAY_ACTIVE_TIME)   

    def clear_gpio(self):
        print('Clear GPIO')
        gpio.cleanup()

    
