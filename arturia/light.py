from typing import Literal
import time

from arturia.dispatch import send_to_device
import arturia.config


"""Import from FL Studio library"""
import device
import utils

ESSENTIAL_KEYBOARD = 'mkII' not in device.getName()
MKII_88_KEYBOARD = 'mkII 88' in device.getName()
MKII_49_KEYBOARD = 'mkII 49' in device.getName()

class DeviceLights:
    """Maintains setting all the button lights on the Arturia device."""
    # Value for turning on/off an LED.
    LED_ON: int = 127
    LED_OFF: int = 0
    
    MISSING: int = 0
    
    # IDs for all of the buttons with lights
    ID_OCTAVE_MINUS             = 16
    ID_OCTAVE_PLUS              = 17
    ID_CHORD                    = 18
    ID_TRANSPOSE                = 19
    ID_MIDI_CHANNEL             = 20
    ID_PAD_MODE_CHORD_TRANSPOSE = 21
    ID_PAD_MODE_CHORD_MEMORY    = 22
    ID_PAD_MODE_PAD             = 23
    ID_NAVIGATION_CATEGORY      = 24
    ID_NAVIGATION_PRESET        = 25
    ID_NAVIGATION_LEFT          = 26
    ID_NAVIGATION_RIGHT         = 27
    ID_NAVIGATION_ANALOG_LAB    = 28
    ID_NAVIGATION_DAW           = 29
    ID_NAVIGATION_USER          = 30
    ID_BANK_NEXT                = 31
    ID_BANK_PREVIOUS            = 32
    ID_BANK_TOGGLE              = 33
    
    # Program bank buttons (these are the channel select buttons). Last button is the master/multi button
    ARRAY_IDS_BANK_SELECT: list[int] = [34, 35, 36, 37, 38, 39, 40, 41, 42]
    
    # Track Controls
    ID_TRACK_SOLO   = 96
    ID_TRACK_MUTE   = 97
    ID_TRACK_RECORD = 98
    ID_TRACK_READ   = 99
    ID_TRACK_WRITE  = 100
    
    # Global controls
    ID_GLOBAL_SAVE  = 101
    ID_GLOBAL_IN    = 102
    ID_GLOBAL_OUT   = 103
    ID_GLOBAL_METRO = 104
    ID_GLOBAL_UNDO  = 105
    
    # Transports section
    ID_TRANSPORTS_REWIND    = 106
    ID_TRANSPORTS_FORWARD   = 107
    ID_TRANSPORTS_STOP      = 108
    ID_TRANSPORTS_PLAY      = 109
    ID_TRANSPORTS_RECORD    = 110
    ID_TRANSPORTS_LOOP      = 111
    
    # 4x4 lookup for the pad ids.
    MATRIX_IDS_PAD: list[list[int]] = [
        [112, 113, 114, 115],
        [116, 117, 118, 119],
        [120, 121, 122, 123],
        [124, 125, 126, 127],
    ]
    
    # Command bytes for setting monochrome light (followed by id, 7-bit LED value)
    SET_MONOCHROME_LIGHT_COMMAND: bytes = bytes([0x02, 0x00, 0x10])
    
    # Command bytes for setting RGB light (followed by id, 7-bit R, 7-bit G, 7-bit B)
    SET_RGB_LIGHT_COMMAND: bytes = bytes([0x02, 0x00, 0x16])
    
    def __init__(self, send_fn=None):
        if send_fn is None:
            send_fn = send_to_device
        self.send_fn = send_fn

        # Map of last send times
        self.last_send_ms = {}
        
    @staticmethod
    def AsOnOffByte(is_on: bool):
        """Converts a boolean to the corresponding on/off to use in the method calls of this class."""
        return DeviceLights.LED_ON if is_on else DeviceLights.LED_OFF
    
    @staticmethod
    def get_zero_matrix(zero: Literal[0] = 0) -> list[list[int]]:
        num_rows: int = len(DeviceLights.MATRIX_IDS_PAD)
        num_cols: int = len(DeviceLights.MATRIX_IDS_PAD[0])
        return [[zero]*num_cols for _ in range(num_rows)]

    @staticmethod
    def rgb2int(red, green, blue) -> bytes:
        bitmask = 0xFF
        red     &= bitmask
        green   &= bitmask
        blue    &= bitmask
        return (red << 16) | (green << 8) | blue
    
    @staticmethod
    def int2rgb(value):
        bitmask = 0xFF
        red     = (value >> 16) & bitmask
        green   = (value >> 8) & bitmask
        blue    = value & bitmask
        return red, green, blue
    
    @staticmethod
    def to7bit(value) -> int:
        return int(float(value) * (127.0 / 255.0))
    
    @staticmethod
    def to7bitColor(color) -> bytes:
        r, g, b = DeviceLights.int2rgb(color)
        r = DeviceLights.to7bit(r)
        g = DeviceLights.to7bit(g)
        b = DeviceLights.to7bit(b)
        return DeviceLights.rgb2int(r, g, b)
    
    @staticmethod
    def mapToClosestHue(rgb, sat=0.7, value=0.02, maxrgb=127):
        h, _, _ = utils.RGBToHSVColor(rgb)
        s = sat
        v = value
        r, g, b = utils.HSVtoRGB(h, s, v)
        return DeviceLights.rgb2int(int(maxrgb*r), int(maxrgb*g), int(maxrgb*b))
    
    @staticmethod
    def fadedColor(rgb):
        return DeviceLights.mapToClosestHue(rgb, sat=1.0, value=0.02, maxrgb=127)

    @staticmethod
    def fullColor(rgb):
        return DeviceLights.mapToClosestHue(rgb, sat=1.0, value=0.2, maxrgb=127)

    @staticmethod
    def get_pad_led_id(button_id: int):
        MIDI_DRUM_PAD_DATA1_MIN = 36

        if MKII_88_KEYBOARD or MKII_49_KEYBOARD or config.INVERT_LED_LAYOUT:
            # On 49/88 keyboard, the button IDs are flipped:
            # 0x30, 0x31, 0x32, 0x33
            # 0x2C, 0x2D, 0x2E, 0x2F
            # 0x28, 0x29, 0x30, 0x31
            # 0x24, 0x25, 0x26, 0x27
            idx = button_id - MIDI_DRUM_PAD_DATA1_MIN
            col = idx % 4
            row = 3 - (idx // 4)
            return DeviceLights.MATRIX_IDS_PAD[row][col]
        return button_id - MIDI_DRUM_PAD_DATA1_MIN + DeviceLights.MATRIX_IDS_PAD[0][0]

    def set_pad_lights(self, matrix_values, rgb: bool = False) -> None:
        """ Set the pad lights given a matrix of color values to set the pad with.
        :param matrix_values: 4x4 array of arrays containing the LED color values.
        """
        # Note: Pad lights can be set to RGB colors, but this doesn't seem to be working.
        led_map: dict = {}
        num_rows: int = len(DeviceLights.MATRIX_IDS_PAD)
        num_cols: int = len(DeviceLights.MATRIX_IDS_PAD[0])
        for r in range(num_rows):
            for c in range(num_cols):
                led_map[DeviceLights.MATRIX_IDS_PAD[r][c]] = matrix_values[r][c]

        self.set_pad_lights(led_map, rgb)
    
    def set_lights(self, led_mapping, rgb: bool=False):
        """ Given a map of LED ids to color value, construct and send a command with all the led mapping. """
        time_ms = time.monotonic() * 1000
        for led_id, led_value in led_mapping.items():
            # Do not toggle/set lights that are missing
            if led_id == DeviceLights.MISSING: continue
                
            if led_id not in self.last_send_ms:
                self.last_send_ms[led_id] = 0
            
            # Drop value
            if time_ms - self.last_send_ms[led_id] < 33: continue
                
            self.last_send_ms[led_id] = time_ms
            
            if rgb:
                r, g, b = DeviceLights.int2rgb(led_value)
                self.send_fn(DeviceLights.SET_RGB_LIGHT_COMMAND + bytes([led_id, r, g, b]))
            else:
                self.send_fn(DeviceLights.SET_MONOCHROME_LIGHT_COMMAND + bytes([led_id, led_value]))
            
            # Need to intentionally sleep to allow time for keyboard to process command sent.
            time.sleep(0.0001)
            
    
    def set_bank_lights(self, array_values, rgb: bool=False):
        """ Set the bank lights given an array of color values to set the bank lights with.

        :param array_values: a 9-element array containing the LED color values.
        """
        if not DeviceLights.ARRAY_IDS_BANK_SELECT: return
        
        led_map = {k: v for k, v in zip(DeviceLights.ARRAY_IDS_BANK_SELECT, array_values)}
        self.set_lights(led_map, rgb)
    