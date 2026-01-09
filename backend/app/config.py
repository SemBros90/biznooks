import os
from typing import Optional


class Settings:
    def __init__(self):
        self.GSP_BASE_URL: Optional[str] = os.getenv('GSP_BASE_URL')
        # Leave sandbox unset by default so local demos use the simulated GSTN
        self.GSP_SANDBOX_URL: Optional[str] = os.getenv('GSP_SANDBOX_URL')
        self.GSP_CLIENT_ID: Optional[str] = os.getenv('GSP_CLIENT_ID')
        self.GSP_PRIVATE_KEY_PATH: Optional[str] = os.getenv('GSP_PRIVATE_KEY_PATH')
        self.GSP_PUBLIC_KEY_PATH: Optional[str] = os.getenv('GSP_PUBLIC_KEY_PATH')
        self.GSP_TIMEOUT: int = int(os.getenv('GSP_TIMEOUT', '10'))
        self.GSP_RETRIES: int = int(os.getenv('GSP_RETRIES', '3'))
        self.GSP_BACKOFF_FACTOR: float = float(os.getenv('GSP_BACKOFF_FACTOR', '1.5'))
        # Optional Redis URL for background queue (RQ). If unset, tasks run synchronously.
        self.REDIS_URL: Optional[str] = os.getenv('REDIS_URL')
        self.GSP_QUEUE_NAME: Optional[str] = os.getenv('GSP_QUEUE_NAME', 'gsp')


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
