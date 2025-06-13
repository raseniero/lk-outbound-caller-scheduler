import logging
import pytest
from unittest.mock import patch, MagicMock
import mytimer.__init__ as mytimer_mod

def test_timer_logs_message(caplog):
    # Arrange: Patch the logger and create a mock TimerRequest
    mock_timer = MagicMock()
    with caplog.at_level(logging.INFO):
        # Act: Call the timer function
        mytimer_mod.main(mock_timer)
    # Assert: Check that the expected log message is present
    assert any('[mytimer] Timer triggered at' in message for message in caplog.messages), (
        'Expected timer log message not found in logs.'
    )
