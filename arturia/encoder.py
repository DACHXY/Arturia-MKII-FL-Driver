from arturia import light, dispatch, config
from arturia.light import DeviceLights
from arturia.display import DeviceDisplay

"""Import from FL Studio library"""
import channels
import device
import general
import midi
import mixer
import patterns
import transport
import ui

SCRIPT_VERSION = general.getVersion()

if SCRIPT_VERSION >= 8:
    import plugins

def get_param_names(plugin_idx):
    return [plugins.getParamName(i, plugin_idx).lower() for i in range(plugins.getParamCount(plugin_idx))]

def find_parameter_index(parameter_names, *keywords):
    candidates = set(enumerate(parameter_names))
    for keyword in keywords:
        keyword = keyword.lower()
        if len(candidates) <= 1: break
        
        next_candidates = []
        for val in candidates:
            if keyword in val[1]:
                next_candidates.append(val)
        candidates = next_candidates
    return candidates[0][0] if candidates else -1

def generate_knobs_mapping(plugin_idx):
    if SCRIPT_VERSION < 8:
        return False
    
    params = get_param_names(plugin_idx)
    map_idx = [
        find_parameter_index(params, 'cutoff', 'filter', '1'),
        find_parameter_index(params, 'resonance', 'filter', '1'),
        find_parameter_index(params, 'lfo', 'delay', '1'),
        find_parameter_index(params, 'lfo', 'rate', '1'),
        find_parameter_index(params, 'macro', '1'),
        find_parameter_index(params, 'macro', '2'),
        find_parameter_index(params, 'macro', '3'),
        find_parameter_index(params, 'macro', '4'),
        find_parameter_index(params, 'chorus'),
    ]
    for idx in map_idx:
        if idx >= 0:
            return map_idx
    return []

class DeviceInputControls:
    """ Manges what the sliders/knobs control on an Arturia Keyboard.

    On the Arturia KeyLab 61 Keyboard, there is a row of 9 encoders and 9 sliders. Plugins may have
    more than 9 encoders/sliders. As such, we will allow mapping the Next/Previous buttons to
    different "pages".
    """
    INPUT_MODE_CHANNEL_PLUGINS = 0
    INPUT_MODE_MIXER_OVERVIEW = 1
    MODE_NAMES = {
        INPUT_MODE_CHANNEL_PLUGINS: 'Channel Plugin',
        INPUT_MODE_MIXER_OVERVIEW: 'Mixer Panel',
    }
    MAX_NUM_PAGES = 16   # Bank 0-F for plugins and 0 - 127 for mixer

    @staticmethod
    def to_rec_value(value, limit=midi.FromMIDI_Max):
        return int((value / 127.0) * limit)
    
    def set_mixer_param(self, param_id, value, incremental=False, track_index=0, plugin_index=0):
        event_id = mixer.getTrackPluginId(track_index, plugin_index) + param_id
        if incremental:
            value = channels.incEventValue(event_id, value, 0.01)
        else:
            max_val = int(12800 * config.MAX_MIXER_VOLUME / 100.0)
            value = DeviceInputControls.to_rec_value(value, limit=max_val)
            
        general.processRECEvent(
            event_id, value, midi.REC_UpdateValue | midi.REC_UpdatePlugLabel | midi.REC_ShowHint
            | midi.REC_UpdateControl | midi.REC_SetChanged
        ) 
        
        if incremental:
            self.check_and_show_hint()
    
    def check_and_show_hint():
        print()