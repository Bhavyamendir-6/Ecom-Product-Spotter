import logging
import os
import time
from pathlib import Path
from contextvars import ContextVar
from typing import Any

_model_call_stack: ContextVar[list] = ContextVar("model_call_stack", default=[])
_agent_run_stack: ContextVar[list] = ContextVar("agent_run_stack", default=[])


def setup_logging(log_dir: str = None, log_level: str = "INFO") -> None:
    if log_dir is None:
        log_dir = str(Path(__file__).resolve().parent / "logs")
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    fh = logging.FileHandler(os.path.join(log_dir, "agent.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    logger.addHandler(fh)
    logger.addHandler(logging.StreamHandler())


def before_model_callback(callback_context: Any, llm_request: Any, **kwargs) -> None:
    stack = list(_model_call_stack.get())
    stack.append(time.time())
    _model_call_stack.set(stack)


def after_model_callback(callback_context: Any, llm_response: Any, **kwargs) -> None:
    stack = list(_model_call_stack.get())
    start = stack.pop() if stack else None
    _model_call_stack.set(stack)
    duration_ms = int((time.time() - start) * 1000) if start else None
    response_size = 0
    if llm_response and llm_response.content and llm_response.content.parts:
        response_size = sum(
            len(p.text) for p in llm_response.content.parts if p.text
        )
    logging.getLogger(__name__).info(
        "model_call duration_ms=%s response_size=%s", duration_ms, response_size
    )


def before_agent_callback(callback_context: Any, **kwargs) -> None:
    agent_name = getattr(
        getattr(callback_context, "agent", None), "name", "unknown"
    ) or "unknown"
    stack = list(_agent_run_stack.get())
    stack.append((agent_name, time.time()))
    _agent_run_stack.set(stack)
    logging.getLogger(__name__).info("agent_run_start agent=%s", agent_name)


def after_agent_callback(callback_context: Any, **kwargs) -> None:
    stack = list(_agent_run_stack.get())
    if stack:
        agent_name, start = stack.pop()
        _agent_run_stack.set(stack)
        duration_ms = int((time.time() - start) * 1000)
        logging.getLogger(__name__).info(
            "agent_run_end agent=%s duration_ms=%s", agent_name, duration_ms
        )
