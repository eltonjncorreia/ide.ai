"""
Status indicators — visual feedback for AI streaming, errors, and idle states.

Uses subtle Unicode symbols for professional appearance:
- Streaming: ◐ (one character, less aggressive than ⏳)
- Error: ✗ (clear error state)
- Success: ✓ (operation complete)
- Idle: · (neutral, subtle)
"""


class StatusIndicators:
    """Status indicator symbols for UI states."""

    # Streaming/Loading states
    STREAMING = "◐"      # One-character indicator (less aggressive)
    LOADING = "◐"        # Alias for streaming
    
    # Error states
    ERROR = "✗"          # Clear error indication
    
    # Success/Idle states
    SUCCESS = "✓"        # Operation complete
    IDLE = "·"           # Neutral/ready state (single dot, subtle)
    
    # Terminal states
    TERMINAL_BUSY = "◐"  # Command running
    TERMINAL_IDLE = "$"  # Shell ready (keep traditional prompt)

    @staticmethod
    def get_streaming() -> str:
        """Get streaming indicator."""
        return StatusIndicators.STREAMING

    @staticmethod
    def get_error() -> str:
        """Get error indicator."""
        return StatusIndicators.ERROR

    @staticmethod
    def get_success() -> str:
        """Get success indicator."""
        return StatusIndicators.SUCCESS

    @staticmethod
    def get_idle() -> str:
        """Get idle indicator."""
        return StatusIndicators.IDLE

    @staticmethod
    def get_terminal_busy() -> str:
        """Get terminal busy indicator."""
        return StatusIndicators.TERMINAL_BUSY

    @staticmethod
    def get_terminal_idle() -> str:
        """Get terminal idle indicator."""
        return StatusIndicators.TERMINAL_IDLE
