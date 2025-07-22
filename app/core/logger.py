"""
Logging configuration and utilities for the Interview Agent application.
Provides a centralized logging system with consistent formatting and multiple output handlers.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import json
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class InterviewAgentLogger:
    """Centralized logger for the Interview Agent application."""
    
    def __init__(self, name: str = "interview_agent"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logger with handlers and formatters."""
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Console Handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File Handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            filename=logs_dir / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # JSON Handler for structured logging
        json_handler = logging.handlers.RotatingFileHandler(
            filename=logs_dir / "app.json",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_formatter = JSONFormatter()
        json_handler.setFormatter(json_formatter)
        
        # Error Handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            filename=logs_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(funcName)s | %(message)s\n%(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(json_handler)
        self.logger.addHandler(error_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance with the specified name."""
        if name:
            return logging.getLogger(f"{self.name}.{name}")
        return self.logger
    
    def log_function_call(self, func_name: str, args: dict = None, kwargs: dict = None):
        """Log function call with parameters."""
        params = []
        if args:
            params.extend([str(arg) for arg in args])
        if kwargs:
            params.extend([f"{k}={v}" for k, v in kwargs.items()])
        
        self.logger.debug(f"Function call: {func_name}({', '.join(params)})")
    
    def log_function_result(self, func_name: str, result: any):
        """Log function result."""
        self.logger.debug(f"Function result: {func_name} -> {result}")
    
    def log_api_request(self, method: str, path: str, status_code: int, duration: float):
        """Log API request details."""
        level = logging.INFO if status_code < 400 else logging.WARNING
        self.logger.log(level, f"API {method} {path} -> {status_code} ({duration:.3f}s)")
    
    def log_llm_call(self, model: str, prompt_length: int, response_length: int, duration: float):
        """Log LLM API call details."""
        self.logger.info(f"LLM call: {model} | Prompt: {prompt_length} chars | Response: {response_length} chars | Duration: {duration:.3f}s")
    
    def log_vector_search(self, query: str, results_count: int, duration: float):
        """Log vector search operations."""
        self.logger.info(f"Vector search: '{query[:50]}...' -> {results_count} results ({duration:.3f}s)")

# Global logger instance
logger = InterviewAgentLogger()

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance for the specified module."""
    return logger.get_logger(name)

# Convenience functions for common logging patterns
def log_startup(service_name: str):
    """Log service startup."""
    get_logger().info(f"🚀 Starting {service_name}...")

def log_shutdown(service_name: str):
    """Log service shutdown."""
    get_logger().info(f"🛑 Shutting down {service_name}...")

def log_success(message: str):
    """Log success message."""
    get_logger().info(f"✅ {message}")

def log_warning(message: str):
    """Log warning message."""
    get_logger().warning(f"⚠️ {message}")

def log_error(message: str, exc_info: bool = True):
    """Log error message."""
    get_logger().error(f"❌ {message}", exc_info=exc_info)

def log_info(message: str):
    """Log info message."""
    get_logger().info(f"ℹ️ {message}")

def log_debug(message: str):
    """Log debug message."""
    get_logger().debug(f"🔍 {message}") 