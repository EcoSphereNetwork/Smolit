#!/usr/bin/env python3
import logging
import sys
from agents.core.config import Config
from agents.core.logging_config import setup_logger

def main():
    # Setup logging
    logger = setup_logger()
    logger.setLevel(logging.DEBUG)

    # Initialize config
    config = Config()

    # Try to start Llama server
    logger.info("Testing Llama server startup...")
    logger.info("This may take several minutes if the model needs to be downloaded (~900MB)")
    
    if config.start_llama_server():
        logger.info("Llama server started successfully!")
        
        # Wait for user input before stopping
        try:
            input("Press Enter to stop the server (or Ctrl+C to force quit)...")
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            # Stop server
            config.stop_llama_server()
            logger.info("Llama server stopped")
    else:
        logger.error("Failed to start Llama server")
        sys.exit(1)

if __name__ == "__main__":
    main()

