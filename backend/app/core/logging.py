import logging
import sys
import os
from typing import Dict, Any, Optional
import structlog
from datetime import datetime


def configure_logging(
    app_name: str = "abts-unified-generator",
    log_level: str = "INFO",
    json_logs: bool = False,
) -> None:
    """
    Configure logging for the application
    
    Args:
        app_name: Name of the application for logs
        log_level: Logging level
        json_logs: Whether to output logs in JSON format
    """
    level = getattr(logging, log_level.upper())
    
    # Create processors list - reordered to prevent the 'tuple' object deletion issue
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add the formatter wrapper as the last processor
    renderer_processor = structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    
    # Configure structlog with safer processor chain
    structlog.configure(
        processors=processors + [renderer_processor],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create formatter
    if json_logs:
        formatter = structlog.processors.JSONRenderer()
    else:
        formatter = structlog.dev.ConsoleRenderer(colors=True)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Fix for tuple object deletion issue with remove_processors_meta
    foreign_pre_chain = list(processors)  # Make a copy to avoid referencing the same list
    
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=formatter,
            foreign_pre_chain=foreign_pre_chain,
        )
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)
    
    # Set log level for specific loggers
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("fastapi").setLevel(level)
    
    # Set watchfiles logger to a higher level to avoid spam
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    
    # Set debug level for our app
    logging.getLogger("app").setLevel(level)
    
    # Log the configuration
    logger = structlog.get_logger(app_name)
    logger.info(
        "Logging configured",
        app_name=app_name,
        log_level=log_level,
        json_logs=json_logs,
    )
    
def get_logger(name: str = "app"):
    """
    Get a structured logger
    
    Args:
        name: Logger name, typically module name
        
    Returns:
        structlog.BoundLogger: A configured structured logger
    """
    return structlog.get_logger(name) 