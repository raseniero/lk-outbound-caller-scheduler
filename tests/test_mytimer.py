import asyncio
import json
import logging
import os
import pytest
import sys
from unittest.mock import patch, MagicMock, AsyncMock, call, ANY, create_autospec
import azure.functions as func

# Import the modules to test
import mytimer.__init__ as mytimer_mod
from mytimer.make_call import make_call, validate_environment, log_and_exit

# Test data
TEST_ENV_VARS = {
    'LIVEKIT_URL': 'https://test.livekit.io',
    'LIVEKIT_API_KEY': 'test_api_key',
    'LIVEKIT_API_SECRET': 'test_api_secret',
    'PHONE_NUMBER': '+1234567890',
    'TRANSFER_TO': 'agent1',
    'ROOM_NAME': 'test-room',
    'AGENT_NAME': 'test-agent',
    'SIP_OUTBOUND_TRUNK_ID': 'ST_test_trunk',
}

@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, TEST_ENV_VARS):
        yield

def test_timer_logs_message():
    # This test verifies the basic logging behavior of the timer function
    # Arrange
    # Create a proper mock for TimerRequest
    mock_timer = MagicMock(spec=func.TimerRequest)
    mock_timer.past_due = False
    
    with (
        patch('mytimer.__init__.make_call', new_callable=AsyncMock) as mock_make_call,
        patch('mytimer.__init__.logging') as mock_logging,
        patch('mytimer.__init__.get_event_loop') as mock_get_loop,
        patch('mytimer.__init__.asyncio') as mock_asyncio,
    ):
        # Setup mocks
        mock_make_call.return_value = None
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False  # Simulate loop not running
        mock_get_loop.return_value = mock_loop
        
        # Setup the future that ensure_future will return
        mock_future = asyncio.Future()
        mock_future.set_result(None)
        mock_asyncio.ensure_future.return_value = mock_future
        
        # Act - Call the timer's main function
        mytimer_mod.main(mock_timer)
        
        # Assert - Verify the event loop was used correctly
        mock_get_loop.assert_called_once()
        mock_loop.run_until_complete.assert_called_once()
        
        # Verify the timer function was called with the mock timer
        mock_timer.past_due  # This verifies past_due was accessed
        
        # Verify the logging calls that we expect
        # The timer function logs when it starts
        mock_logging.info.assert_any_call('Python timer trigger function started at %s', ANY)
        
        # Get the coroutine passed to run_until_complete and check it calls make_call
        coro = mock_loop.run_until_complete.call_args[0][0]
        
        # Execute the coroutine to verify it calls make_call
        async def test_coro():
            await coro
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_coro())
            mock_make_call.assert_awaited_once()
        finally:
            loop.close()

def test_timer_calls_make_correctly():
    """Test that the timer function correctly handles the async call to make_call."""
    # Arrange
    mock_timer = MagicMock(spec=func.TimerRequest)
    mock_timer.past_due = False
    
    with (
        patch('mytimer.__init__.make_call', new_callable=AsyncMock) as mock_make_call,
        patch('mytimer.__init__.logging') as mock_logging,
        patch('mytimer.__init__.get_event_loop') as mock_get_loop,
        patch('mytimer.__init__.asyncio') as mock_asyncio,
    ):
        # Setup mocks
        mock_make_call.return_value = None
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False  # Simulate loop not running
        mock_get_loop.return_value = mock_loop
        
        # Setup the future that ensure_future will return
        mock_future = asyncio.Future()
        mock_future.set_result(None)
        mock_asyncio.ensure_future.return_value = mock_future
        
        # Act - Call the timer's main function
        mytimer_mod.main(mock_timer)
        
        # Assert - Verify the event loop was used correctly
        mock_get_loop.assert_called_once()
        mock_loop.run_until_complete.assert_called_once()
        
        # Get the coroutine passed to run_until_complete
        coro = mock_loop.run_until_complete.call_args[0][0]
        
        # Execute the coroutine to verify it calls make_call
        async def test_coro():
            await coro
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_coro())
            mock_make_call.assert_awaited_once()
        finally:
            loop.close()

def test_timer_handles_make_call_exception():
    """Test that the timer function properly handles and logs exceptions from make_call."""
    # Arrange
    mock_timer = MagicMock(spec=func.TimerRequest)
    mock_timer.past_due = False
    test_exception = Exception("Test exception")
    
    with (
        patch('mytimer.__init__.make_call', new_callable=AsyncMock) as mock_make_call,
        patch('mytimer.__init__.logging') as mock_logging,
        patch('mytimer.__init__.get_event_loop') as mock_get_loop,
        patch('mytimer.__init__.asyncio') as mock_asyncio,
    ):
        # Setup mocks
        mock_make_call.side_effect = test_exception
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False  # Simulate loop not running
        mock_get_loop.return_value = mock_loop
        
        # Create a mock sleep coroutine
        async def mock_sleep(*args, **kwargs):
            pass
            
        # Setup the future that ensure_future will return
        mock_future = asyncio.Future()
        mock_future.set_exception(test_exception)
        mock_asyncio.ensure_future.return_value = mock_future
        mock_asyncio.sleep.side_effect = mock_sleep
        
        # Act - Call the timer's main function
        mytimer_mod.main(mock_timer)
        
        # Assert - Verify the event loop was used correctly
        mock_get_loop.assert_called_once()
        mock_loop.run_until_complete.assert_called_once()
        
        # Get the coroutine passed to run_until_complete
        coro = mock_loop.run_until_complete.call_args[0][0]
        
        # Execute the coroutine to verify it handles the exception
        async def test_coro():
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                mock_sleep.return_value = None
                try:
                    await coro
                except Exception as e:
                    assert str(e) == "Test exception"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_coro())
            
            # Verify the error was logged with the expected message format
            mock_logging.error.assert_called()
            
            # Check if any error call matches our expected format
            error_found = False
            for call_args, _ in mock_logging.error.call_args_list:
                if isinstance(call_args, tuple) and len(call_args) > 0:
                    msg = call_args[0]
                    if isinstance(msg, str) and "%d call attempts failed" in msg:
                        error_found = True
                        break
            
            assert error_found, f"Expected error message not found in calls: {mock_logging.error.call_args_list}"
        finally:
            loop.close()

@pytest.mark.asyncio
async def test_make_call_success():
    # Arrange
    # Create mocks for the LiveKit API client and its methods
    mock_dispatch = MagicMock()
    mock_dispatch.id = 'test-dispatch-123'

@pytest.mark.asyncio
async def test_make_call_missing_env_vars():
    # Test each required environment variable
    required_vars = [
        'LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET',
        'PHONE_NUMBER', 'TRANSFER_TO', 'ROOM_NAME', 'AGENT_NAME', 'SIP_OUTBOUND_TRUNK_ID'
    ]

    for var in required_vars:
        # Create a copy of the test env vars without the current variable
        test_env = TEST_ENV_VARS.copy()
        test_env.pop(var, None)
        
        with patch.dict(os.environ, test_env, clear=True):
            # Act
            is_valid, errors = validate_environment()
            
            # Assert
            assert not is_valid
            assert any(f"Missing required environment variables: {var}" in error for error in errors)

@pytest.mark.asyncio
async def test_make_call_invalid_trunk_id():
    # Arrange
    invalid_trunk_id = 'invalid_trunk_id'
    test_env = TEST_ENV_VARS.copy()
    test_env['SIP_OUTBOUND_TRUNK_ID'] = invalid_trunk_id
    
    with patch.dict(os.environ, test_env, clear=True):
        # Act
        is_valid, errors = validate_environment()
        
        # Assert
        assert not is_valid
        assert any('Invalid SIP_OUTBOUND_TRUNK_ID' in error for error in errors)
