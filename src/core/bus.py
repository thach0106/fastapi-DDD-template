from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, TypeVar, Generic, Callable, Awaitable
import logging

# Type definitions
C = TypeVar("C")  # Command Type
R = TypeVar("R")  # Result Type
Q = TypeVar("Q")  # Query Type

logger = logging.getLogger(__name__)

class Message(ABC):
    """Base interface for Commands and Queries."""
    pass

# --- Middlewares ---

Middleware = Callable[[Message, Callable[[Message], Awaitable[Any]]], Awaitable[Any]]

class Bus(Generic[C, R]):
    def __init__(self):
        self._handlers: Dict[Type[C], Callable[[C], Awaitable[R]]] = {}
        self._middlewares: List[Middleware] = []

    def register(self, message_type: Type[C], handler: Callable[[C], Awaitable[R]]):
        self._handlers[message_type] = handler

    def add_middleware(self, middleware: Middleware):
        self._middlewares.append(middleware)

    async def dispatch(self, message: C) -> R:
        handler = self._handlers.get(type(message))
        if not handler:
            raise ValueError(f"No handler registered for {type(message)}")

        # Chain middlewares
        async def wrapped_handler(msg: C) -> R:
            return await handler(msg)

        # Apply middlewares in reverse order so the first added is the outer-most
        pipeline = wrapped_handler
        for mw in reversed(self._middlewares):
             # Closure to capture current middleware and next step
            def make_pipe(current_mw, next_step):
                async def pipe_step(msg):
                    return await current_mw(msg, next_step)
                return pipe_step
            
            pipeline = make_pipe(mw, pipeline)

        return await pipeline(message)

# --- Concrete Buses ---

class CommandBus(Bus[Any, Any]):
    pass

class QueryBus(Bus[Any, Any]):
    pass

# --- Standard Middlewares ---

async def logging_middleware(message: Message, next_step: Callable[[Message], Awaitable[Any]]) -> Any:
    msg_type = type(message).__name__
    logger.info(f"Dispatching {msg_type}: {message}")
    try:
        result = await next_step(message)
        logger.info(f"Completed {msg_type}")
        return result
    except Exception as e:
        logger.error(f"Failed {msg_type}: {e}")
        raise
