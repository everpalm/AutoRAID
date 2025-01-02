# Contents of device_under_testing.py
'''Copyright (c) 2024 Jaron Cheng'''
import RPi.GPIO as gpio
import logging
import time
import json

logger = logging.getLogger(__name__)


class RaspBerryPins:
    """
    Singleton class for defining Raspberry Pi GPIO pins.

    This class reads pin definitions from a JSON configuration file and
    provides access to the physical pin number for specific functions. Only
    one instance of this class can exist, ensuring consistent pin assignments
    across the application.

    Attributes:
        pin_define_file (str): The name of the JSON file containing pin
        definitions.
        _pin_define (str): The key in the JSON file to retrieve the pin
        configuration.
        power_switch (int): The physical pin number associated with the power
        switch.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of the class is created (Singleton pattern).

        Returns:
            RaspBerryPins: The singleton instance of the RaspBerryPins class.
        """
        if cls._instance is None:
            cls.instance = super(RaspBerryPins, cls).__new__(cls)
        return cls.instance

    def __init__(self, pin_define_file, pin_define):
        """
        Initializes the RaspBerryPins class with the pin definition file and
        key.

        Args:
            pin_define_file (str): The name of the JSON file containing pin
            definitions.
            pin_define (str): The key in the JSON file to retrieve the pin
            configuration.
        """
        self.pin_define_file = pin_define_file
        self._pin_define = pin_define
        self.power_switch = self.get_gpio()
        self._initialized = True

    def get_gpio(self):
        """
        Retrieves the physical GPIO pin number based on the pin definition.

        Reads the pin definition from the JSON file and extracts the physical
        pin number associated with the provided key.

        Returns:
            int: The physical GPIO pin number.

        Raises:
            IOError: Raised if the pin definition file cannot be opened or
            read.
            This exception is propagated to the caller, ensuring the issue is
            handled appropriately in the calling context.
        """
        try:
            with open(f'config/{self.pin_define_file}', 'r') as f:
                dict_pin_define = json.load(f)
                logger.debug('dict_pin_define = %s', dict_pin_define)
                temp = dict_pin_define.get(self._pin_define)
                logger.debug('temp["physical_pin"] = %s', temp["physical_pin"])
                return temp["physical_pin"]

        except IOError:
            logger.error('Cannot open/read file: %s', self.pin_define_file)
            raise


class OperateGPIO:
    """
    Class for operating GPIO pins on a Raspberry Pi.

    This class provides methods to interact with GPIO pins, specifically for
    controlling a power switch via a relay. It supports setting the GPIO mode,
    pressing and holding the power button, and cleaning up GPIO states.

    Attributes:
        RELAY_ACTIVE_TIME (int): The time in seconds to activate the relay.
        HOLD_BUTTON_TIME (int): The time in seconds to hold the power button.
        switch_pin (int): The physical pin number for the power switch.
        _board_mode (int): The GPIO board mode (e.g., BOARD or BCM).
    """
    RELAY_ACTIVE_TIME = 0.75
    HOLD_BUTTON_TIME = 5

    def __init__(self, pin_define, board_mode):
        """
        Initializes the OperateGPIO class with pin definitions and board mode.

        Args:
            pin_define (RaspBerryPins): The RaspBerryPins instance providing
            pin definitions.
            board_mode (int): The GPIO board mode (BOARD or BCM).

        Raises:
            RuntimeError: Raised if an invalid GPIO mode is specified or if
            there's an issue setting up the GPIO pins. This ensures the
            initialization process is robust and any configuration errors are
            surfaced immediately.
        """
        self.switch_pin = pin_define.power_switch
        logger.debug('self.switch_pin = %s', self.switch_pin)
        self._board_mode = board_mode
        gpio.setmode(self._board_mode)

        # Relay is active low
        gpio.setup(self.switch_pin, gpio.OUT, initial=gpio.HIGH)
        time.sleep(self.RELAY_ACTIVE_TIME)

    @property
    def board_mode(self):
        """
        Gets the current GPIO board mode.

        Returns:
            int: The current GPIO board mode.
        """
        return self._board_mode

    @board_mode.setter
    def board_mode(self, value):
        """
        Sets a new GPIO board mode and updates the mode if it differs from the
        current mode.

        Args:
            value (int): The new GPIO board mode.

        Raises:
            ValueError: Raised if an invalid GPIO mode is provided. This helps
            ensure that only valid modes are set, preventing misconfigurations.
        """
        if self._board_mode != value:
            try:
                gpio.setmode(value)
                self._board_mode = gpio.getmode()

            except ValueError as e:
                logger.error('Invalid GPIO mode: %s', {e})
                raise

    def _set_switch_mode(self):
        """
        Sets the GPIO mode and prepares the switch pin for operation.

        Ensures that the GPIO mode is set to BOARD before operating the switch
        pin.

        Raises:
            RuntimeError: Raised if there is an issue setting the GPIO mode or
            preparing the switch pin. This ensures that any hardware setup
            issues are caught and dealt with.
        """
        try:
            mode = gpio.getmode()
            logger.debug(f'self.switch_pin = {self.switch_pin}')
            logger.debug(f'mode = {mode}')
            if mode != gpio.BOARD:
                self.switch_handler()

            # Persist relay for a period of time, not a glitch
            time.sleep(self.RELAY_ACTIVE_TIME)

        except RuntimeError as e:
            logger.error('Failed to set switch mode: %s', {e})
            raise

    def switch_handler(self):
        """
        Configures the GPIO to use the BOARD mode and prepares the switch pin.

        Raises:
            RuntimeError: Raised if there is an issue configuring the GPIO or
            setting up the switch pin. This ensures any setup problems are
            surfaced immediately.
        """
        try:
            gpio.setmode(gpio.BOARD)
            gpio.setup(self.switch_pin, gpio.OUT)
        except RuntimeError as e:
            logger.error('Failed to handle switch: %s', {e})
            raise

    def hold_power_button(self):
        """
        Holds the power button by activating the switch pin for a defined
        period.

        The switch pin is set to LOW, holding the power button for a minimum of
        4 seconds, and then set back to HIGH to avoid floating states.

        Raises:
            RuntimeError: Raised if there is an issue with holding the power
            button, such as a failure in setting the GPIO states. This ensures
            the action is performed as expected or errors are clearly reported.
        """
        try:
            self._set_switch_mode()
            gpio.output(self.switch_pin, gpio.LOW)

            # Hold power button for at least 4 seconds
            time.sleep(self.HOLD_BUTTON_TIME)

            # Must avoid floating and keep HIGH state
            gpio.output(self.switch_pin, gpio.HIGH)

        except RuntimeError as e:
            logger.error('Failed to hold power button: %s', {e})
            raise

    def press_power_button(self):
        """
        Presses the power button by momentarily activating the switch pin.

        The switch pin is set to LOW for a short duration and then set back to
        HIGH to simulate a button press.

        Raises:
            RuntimeError: Raised if there is an issue with pressing the power
            button, such as a failure in setting the GPIO states. This ensures
            the action is performed as expected or errors are clearly reported.
        """
        try:
            self._set_switch_mode()
            gpio.output(self.switch_pin, gpio.LOW)

            # Persist relay for a period of time, not a glitch
            time.sleep(self.RELAY_ACTIVE_TIME)

            # Must avoid floating and keep HIGH state
            gpio.output(self.switch_pin, gpio.HIGH)

        except RuntimeError as e:
            logger.error('Failed to press power button: %s', {e})
            raise

    def clear_gpio(self):
        """
        Cleans up the GPIO settings, resetting all channels that have been
        used.

        This method should be called before the program exits to ensure that
        all GPIO pins are reset to a safe state.

        Raises:
            RuntimeError: Raised if there is an issue with the GPIO cleanup.
            Ensures that the GPIO pins are safely reset even in the presence
            of errors.
        """
        try:
            print('Clear GPIO')
            gpio.cleanup()

        except RuntimeError as e:
            logger.error('Failed to clear GPIO: %s', {e})
            raise
