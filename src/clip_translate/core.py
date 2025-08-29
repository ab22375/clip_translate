"""Core functionality for clip_translate."""

from typing import Any
from pydantic import BaseModel
from loguru import logger


class Config(BaseModel):
    """Application configuration."""
    
    debug: bool = False
    log_level: str = "INFO"
    
    model_config = {"extra": "forbid"}


def setup_logging(config: Config) -> None:
    """Configure logging."""
    logger.remove()
    logger.add(
        "logs/{time}.log",
        rotation="1 day",
        retention="1 week",
        level=config.log_level,
        format="{time} | {level} | {message}",
    )
    if config.debug:
        logger.add(lambda msg: print(msg, end=""), level="DEBUG")
