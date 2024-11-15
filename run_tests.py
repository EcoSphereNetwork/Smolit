#!/usr/bin/env python3
import pytest
import sys
import os
from agents.core.logging_config import setup_logger

def main():
    """Run all tests with coverage report."""
    logger = setup_logger()
    logger.info("Starting test suite...")

    # Add source directory to Python path
    src_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, src_dir)

    # Configure test arguments
    args = [
        "tests",  # test directory
        "-v",     # verbose output
        "--cov=agents",  # coverage for agents package
        "--cov-report=term-missing",  # show lines missing coverage
        "--cov-report=html:coverage_report",  # generate HTML report
        "-W", "ignore::DeprecationWarning",  # ignore deprecation warnings
    ]

    # Run tests
    try:
        logger.info("Running tests...")
        exit_code = pytest.main(args)
        
        if exit_code == 0:
            logger.info("All tests passed successfully!")
        else:
            logger.error(f"Tests failed with exit code: {exit_code}")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

