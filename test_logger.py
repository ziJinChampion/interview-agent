#!/usr/bin/env python3
"""
Test script to demonstrate the logging system functionality.
"""

import time
import random
import logging
from app.core.logger import (
    get_logger, 
    log_startup, 
    log_shutdown, 
    log_success, 
    log_warning, 
    log_error, 
    log_info, 
    log_debug,
    logger
)

def test_basic_logging():
    """Test basic logging functionality."""
    print("=" * 60)
    print("Testing Basic Logging")
    print("=" * 60)
    
    # Get logger for this test
    test_logger = get_logger("test.basic")
    
    # Test different log levels
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    
    # Test convenience functions
    log_startup("Test Service")
    log_success("Operation completed successfully")
    log_warning("Something might be wrong")
    log_error("An error occurred")
    log_info("Here's some information")
    log_debug("Debug information")

def test_function_logging():
    """Test function call and result logging."""
    print("\n" + "=" * 60)
    print("Testing Function Logging")
    print("=" * 60)
    
    def sample_function(param1, param2, keyword_param="default"):
        logger.log_function_call("sample_function", [param1, param2], {"keyword_param": keyword_param})
        
        # Simulate some work
        time.sleep(0.1)
        result = param1 + param2
        
        logger.log_function_result("sample_function", result)
        return result
    
    # Test function logging
    result = sample_function(10, 20, keyword_param="test")
    print(f"Function result: {result}")

def test_api_logging():
    """Test API request logging."""
    print("\n" + "=" * 60)
    print("Testing API Logging")
    print("=" * 60)
    
    # Simulate API requests
    api_requests = [
        ("GET", "/api/health", 200, 0.05),
        ("POST", "/api/interview", 201, 0.15),
        ("GET", "/api/users", 404, 0.02),
        ("PUT", "/api/config", 500, 0.08),
    ]
    
    for method, path, status, duration in api_requests:
        logger.log_api_request(method, path, status, duration)
        time.sleep(0.1)

def test_llm_logging():
    """Test LLM call logging."""
    print("\n" + "=" * 60)
    print("Testing LLM Logging")
    print("=" * 60)
    
    # Simulate LLM calls
    llm_calls = [
        ("gpt-3.5-turbo", 150, 200, 0.8),
        ("gpt-4", 300, 450, 1.2),
        ("claude-3", 200, 300, 0.9),
    ]
    
    for model, prompt_len, response_len, duration in llm_calls:
        logger.log_llm_call(model, prompt_len, response_len, duration)
        time.sleep(0.1)

def test_vector_search_logging():
    """Test vector search logging."""
    print("\n" + "=" * 60)
    print("Testing Vector Search Logging")
    print("=" * 60)
    
    # Simulate vector searches
    searches = [
        ("What is machine learning?", 5, 0.12),
        ("Explain neural networks", 3, 0.08),
        ("How to implement sorting algorithms", 8, 0.25),
    ]
    
    for query, results_count, duration in searches:
        logger.log_vector_search(query, results_count, duration)
        time.sleep(0.1)

def test_error_logging():
    """Test error logging with exceptions."""
    print("\n" + "=" * 60)
    print("Testing Error Logging")
    print("=" * 60)
    
    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception as e:
        log_error(f"Caught exception: {e}")
    
    try:
        # Simulate another error
        result = 1 / 0
    except Exception as e:
        log_error(f"Division by zero error: {e}")

def test_structured_logging():
    """Test structured logging with extra fields."""
    print("\n" + "=" * 60)
    print("Testing Structured Logging")
    print("=" * 60)
    
    # Create a custom logger with extra fields
    custom_logger = get_logger("test.structured")
    
    # Add extra fields to log record
    record = custom_logger.makeRecord(
        "test.structured", 
        logging.INFO, 
        "test_file.py", 
        42, 
        "User action performed", 
        (), 
        None
    )
    record.extra_fields = {
        "user_id": "12345",
        "action": "login",
        "ip_address": "192.168.1.1",
        "session_id": "abc123"
    }
    
    custom_logger.handle(record)

def main():
    """Run all logging tests."""
    print("🚀 Starting Logger Test Suite")
    print("This will demonstrate all logging features...")
    
    try:
        test_basic_logging()
        test_function_logging()
        test_api_logging()
        test_llm_logging()
        test_vector_search_logging()
        test_error_logging()
        test_structured_logging()
        
        print("\n" + "=" * 60)
        print("✅ All logging tests completed successfully!")
        print("=" * 60)
        print("\n📁 Check the following log files:")
        print("   - logs/app.log (all logs)")
        print("   - logs/app.json (structured JSON logs)")
        print("   - logs/errors.log (error logs only)")
        print("\n🎨 Console output should be colored!")
        
    except Exception as e:
        log_error(f"Test suite failed: {e}")
        raise

if __name__ == "__main__":
    main() 