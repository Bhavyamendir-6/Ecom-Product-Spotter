import pytest
import os
import logging
from unittest.mock import MagicMock, patch

from observability import (
    setup_logging,
    before_model_callback,
    after_model_callback,
    before_agent_callback,
    after_agent_callback,
    _model_call_stack,
    _agent_run_stack,
)


class TestSetupLogging:
    def test_setup_logging_default_dir(self):
        setup_logging()
        # Just verify it doesn't error

    def test_setup_logging_custom_dir(self):
        custom_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_logs_tmp"
        )
        try:
            setup_logging(log_dir=custom_dir)
            assert os.path.isdir(custom_dir)
        finally:
            # Close all file handlers to release locks on Windows
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    root_logger.removeHandler(handler)
            # Clean up
            import shutil
            if os.path.isdir(custom_dir):
                shutil.rmtree(custom_dir, ignore_errors=True)

    def test_setup_logging_custom_level(self):
        setup_logging(log_level="DEBUG")
        # Should not error


class TestModelCallbacks:
    def test_before_model_callback(self):
        ctx = MagicMock()
        req = MagicMock()
        _model_call_stack.set([])
        before_model_callback(ctx, req)
        stack = _model_call_stack.get()
        assert len(stack) == 1
        assert isinstance(stack[0], float)

    def test_after_model_callback_with_start(self):
        ctx = MagicMock()
        resp = MagicMock()
        resp.content.parts = [MagicMock(text="hello")]
        _model_call_stack.set([__import__("time").time()])
        after_model_callback(ctx, resp)
        stack = _model_call_stack.get()
        assert len(stack) == 0

    def test_after_model_callback_empty_stack(self):
        ctx = MagicMock()
        resp = MagicMock()
        resp.content.parts = [MagicMock(text="test")]
        _model_call_stack.set([])
        after_model_callback(ctx, resp)
        # Should not error, duration_ms is None

    def test_after_model_callback_no_content(self):
        ctx = MagicMock()
        resp = MagicMock()
        resp.content = None
        _model_call_stack.set([__import__("time").time()])
        after_model_callback(ctx, resp)

    def test_after_model_callback_none_response(self):
        ctx = MagicMock()
        _model_call_stack.set([__import__("time").time()])
        after_model_callback(ctx, None)


class TestAgentCallbacks:
    def test_before_agent_callback(self):
        ctx = MagicMock()
        ctx.agent.name = "test_agent"
        _agent_run_stack.set([])
        before_agent_callback(ctx)
        stack = _agent_run_stack.get()
        assert len(stack) == 1
        assert stack[0][0] == "test_agent"

    def test_before_agent_callback_no_agent_attr(self):
        ctx = MagicMock(spec=[])  # No attributes
        _agent_run_stack.set([])
        before_agent_callback(ctx)
        stack = _agent_run_stack.get()
        assert stack[0][0] == "unknown"

    def test_after_agent_callback(self):
        import time
        _agent_run_stack.set([("test_agent", time.time())])
        ctx = MagicMock()
        after_agent_callback(ctx)
        stack = _agent_run_stack.get()
        assert len(stack) == 0

    def test_after_agent_callback_empty_stack(self):
        _agent_run_stack.set([])
        ctx = MagicMock()
        after_agent_callback(ctx)
        # Should not error
