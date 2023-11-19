import time

from arturia.dispatch import send_to_device

class DeviceDisplay:
    """Display control"""
    def __init__(self) -> None:
        # line 1 & line 2
        self.line1: str = ' '
        self.line2: str = ' '
        
        # Holds ephemeral text that will expire after the expiration timestamp. These lines will display if the
        # The expiration timestamp is > current timestamp.
        self.ephemeral_line1: str       = ' '
        self.ephemeral_line2: str       = ' '
        self.expiration_time_ms: int    = 0
        
        # line 1 & line 2 start offset
        self.line1_display_offset: int = 0
        self.line2_display_offset: int = 0
        
        # Last timestamp which the text was updated
        self.last_update_ms: int = 0
        
        # Minimum interval before text is scrolled
        self.scroll_interval_ms: int = 500
        
        # How many characters to allow last char to scroll before starting over.
        self.line_end_padding: int = 2
        
        # Track what's currently being displayed
        self.last_display_payload: bytes = bytes()
     
    def get_line1_bytes(self) -> bytearray:
        """Max length: 16 bytes"""
        start_pos: int  = self.line1_display_offset
        end_pos: int    = start_pos + 16
        line: str       = self.line1
        
        # The ephemeral time is not expired
        if self.expiration_time_ms > self.get_timestamp_ms():
            line: str = self.ephemeral_line1
        
        return bytearray(line[start_pos:end_pos], 'ascii')
            
    def get_line2_bytes(self) -> bytearray:
        """Max length: 16 bytes"""
        start_pos: int  = self.line2_display_offset
        end_pos: int    = start_pos + 16
        line: str       = self.line2
        
        # The ephemeral time is not expired
        if self.expiration_time_ms > self.get_timestamp_ms():
            line: str = self.ephemeral_line2
        
        return bytearray(line[start_pos:end_pos], 'ascii')
    
    def get_new_offset(self, start_pos: int, line: str) -> int:
        """Get new offset of line to acheive scrolling effect."""
        end_pos: int = start_pos + 16
        if end_pos >= len(line) + self.line_end_padding or len(line) <= 16:
            return 0
        return start_pos + 1
    
    def update_scroll_pos(self) -> None:
        """Update the position while scrolling"""
        current_time_ms: float = self.get_timestamp_ms()

        # No need to update yet
        if current_time_ms < self.scroll_interval_ms + self.last_update_ms: return
        
        # update the position
        self.line1_display_offset = self.get_new_offset(self.line1_display_offset, self.line1)
        self.line2_display_offset = self.get_new_offset(self.line2_display_offset, self.line2)
        self.last_update_ms = current_time_ms
    
    def refresh_display(self) -> None:
        """Refresh the display screen"""
        data: bytes = bytes([0x04, 0x00, 0x60])
        data += bytes([0x01]) + self.get_line1_bytes() + bytes([0x00])
        data += bytes([0x02]) + self.get_line2_bytes() + bytes([0x00])
        data += bytes([0x7F])
        
        self.update_scroll_pos()
        
        # The last display content not change
        if self.last_display_payload == data: return
        
        # send update msg && update last display payload
        send_to_device(data)
        self.last_display_payload = data
        
    @staticmethod
    def get_timestamp_ms() -> float:
        """ Get the current timestamp in milliseconds"""
        return time.monotonic() * 1000
            
      