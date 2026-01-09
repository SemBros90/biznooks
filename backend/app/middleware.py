from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger("biznooks")


class SimpleRateLimiter(BaseHTTPMiddleware):
    """Very small in-process rate limiter for demo purposes.

    Uses client IP and a basic token-bucket per-process. Not suitable for multi-instance production.
    """

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.tokens = {}

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else 'unknown'
        now = time.time()
        window = 60
        key = client
        state = self.tokens.get(key, {'t': now, 'c': 0})
        # refill logic
        elapsed = now - state['t']
        if elapsed > window:
            state = {'t': now, 'c': 0}
        if state['c'] >= self.calls_per_minute:
            raise HTTPException(status_code=429, detail='Rate limit exceeded')
        state['c'] += 1
        self.tokens[key] = state
        logger.debug(f"RateLimiter: {key} -> {state}")
        response = await call_next(request)
        return response
