"""Import from FL Studio library"""
import device

# Set to True to allow drum pads to light up as a metronome indicator.
ENABLE_PAD_METRONOME_LIGHTS: bool = True

# Set to True to allow transport lights to light up as a metronome indicator.
ENABLE_TRANSPORTS_METRONOME_LIGHTS: bool = True

# Set to True to only allow visual metronome lights when audible metronome in FL Studio is enabled.
# Set to False to always enable visual metronome lights when playing/recording.
METRONOME_LIGHTS_ONLY_WHEN_METRONOME_ENABLED: bool = False

# Set to True to enable piano roll to be focused on during playback/record. This is needed for punch buttons to work.
ENABLE_PIANO_ROLL_FOCUS_DURING_RECORD_AND_PLAYBACK: bool = True

# Configure the port number that midi notes are forwarded to for plugins.
PLUGIN_FORWARDING_MIDI_IN_PORT: int = 10

# Set to True to put display text hints in all caps.
HINT_DISPLAY_ALL_CAPS: bool = False

# Set to True to enable color bank lights. On Essential keyboards, the pad colors are set to the active channel color.
ENABLE_COLORIZE_BANK_LIGHTS: bool = True

# Set True to also colorize the pad lights according to the active color channel (only on MKII. For Essential keyboard,
# the ENABLE_COLORIZE_BANK_LIGHTS sets this option).
ENABLE_COLORIZE_PAD_LIGHTS: bool = True

# If True, then sliders initially control plugin. If False, sliders initially control mixer tracks.
SLIDERS_FIRST_CONTROL_PLUGINS: bool = False

# If True, the sliders are initially ignored until they cross the initial value in the mixer. For example, if mixer
# for track 1 is set to 100% and mixer is at 50%, then mixer sliders won't do anything until they cross or match the
# value of the mixer.
ENABLE_MIXER_SLIDERS_PICKUP_MODE: bool = True

# If True, changes to the controls also update the FL hint panel when appropriate Useful if you can't visually see the
# display on keyboard and need feedback from FL Studio (i.e. plugin active but UI hidden).
ENABLE_CONTROLS_FL_HINTS: bool = True

# If True, then enable turning nav wheel past last pattern to create a new pattern.
ENABLE_PATTERN_NAV_WHEEL_CREATE_NEW_PATTERN: bool = False

# Maximum mixer volume. Set to 120 if you like to overdrive the volume.
# WARNING: You can overdrive this to a larger value, but you may blow out your speaker/headphones if you do not have
# a volume limiter (like some studio monitors). So, do be careful.  I do not recommend values over 120, though it is
# certainly possible.
MAX_MIXER_VOLUME: int = 100

# If True, then long pressing the left/right nav will toggle visibility of mixer/channel rack.
ENABLE_NAV_BUTTON_TOGGLE_VISIBILITY: bool = True

# If True, the pads will assign to the channel rack tracks as follows:
#
#  1   2   3   4
#  5   6   7   8
#  9  10  11  12
# 13  14  15  16
#
# This is useful if you prefer an MPC style assignment where the channel rack tracks contain sample chops.
ENABLE_MPC_STYLE_PADS: bool = False

# If enabled, this will switch the behavior of long pressing on the pads to sustaining the note being played. This
# is particularly useful for MPC style pads that play loops.
# Re-mapping a pad note will still work by holding the record button and pressing the pad button.
ENABLE_LONG_PRESS_SUSTAIN_ON_PADS: bool = False

# If True, this will treat the pad LED layout the same as 88-key which is inverted.
INVERT_LED_LAYOUT: bool = False