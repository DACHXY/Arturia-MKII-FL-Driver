from typing import Callable, Any
import debug

"""Import from FL Studio library"""
import device

class MidiEventDispatcher:
    def __init__(self, transform_fn: Callable) -> None:
        self.transform_fn: Callable                 = transform_fn
        self.dispatch_map: dict[Callable, Callable] = {}
        
    def new_handler(
            self, 
            key, 
            callback_fn: Callable, 
            filter_fn: Callable[[Any], bool] | None = None
        ) -> "MidiEventDispatcher":
        """ Associate a handler function and optional filter predicate function to a key.

        If the transform of the midi event matches the key, then the event is dispatched to the callback function
        given that the filter predicate function also returns true.

        :param key: the result value of transform_fn(event) to match against.
        :param callback_fn: function that is called with the event in the event the transformed event matches.
        :param filter_fn: function that takes an event and returns true if the event should be dispatched. If false
        is returned, then the event is dropped and never passed to callback_fn. Not specifying means that callback_fn
        is always called if transform_fn matches the key.
        """
        def default_true_fn(_) -> bool: return True
        if filter_fn is None: filter_fn = default_true_fn
        self.dispatch_map[key] = (callback_fn, filter_fn)
        return self
        
    def new_handler_for_keys(self, keys, callback_fn: Callable, filter_fn: Callable | None = None) -> "MidiEventDispatcher":
        """ Associate the same handler for a group of keys. See new_handler for more details. """
        for k in keys:
            self.new_handler(k, callback_fn, filter_fn)
        return self
        
    def dispatch(self, event) -> bool:
        """ 
        Dispatches a midi event to the appropriate listener.
        :param event:  the event to dispatch.
        """
        key = self.transform_fn(event)
        processed: bool = False
        if key in self.dispatch_map:
            callback_fn, filter_fn = self.dispatch_map[key]
            event.handled: bool = True
            if filter_fn(event):
                callback_fn(event)
                processed = True
            else:
                debug.log("DISPATCHER", "Event dropped by filter.", event=event)
                processed = True
        else:
            debug.log("DISPATCHER", "No handler found.", event=event)
            
        return processed
    
    
def send_to_device(data) -> None:
    device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42]) + data + bytes([0xF7]))


