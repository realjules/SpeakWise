#!/usr/bin/env python3
"""
Script to run the SpeakWise telephony API server.
This starts the Flask server that handles telephony integration.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import signal
import time

# Add the project root to the path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.integrations.telephony.api import start_api
from src.core.utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(ROOT_DIR, 'telephony_api.log'))
    ]
)
logger = logging.getLogger(__name__)

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal"""
    logger.info("Received SIGTERM signal, shutting down...")
    sys.exit(0)

def main():
    """Run the telephony API server"""
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    parser = argparse.ArgumentParser(description="Run the SpeakWise telephony API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--api-key", help="Pindo API key (overrides configuration)")
    
    args = parser.parse_args()
    
    # If API key provided, update configuration
    if args.api_key:
        try:
            config = Config()
            config.set("telephony", "api_key", args.api_key)
            logger.info("API key set from command line")
        except Exception as e:
            logger.error(f"Error setting API key: {str(e)}")
    
    try:
        logger.info(f"Starting telephony API server on {args.host}:{args.port}")
        start_api(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Shutting down telephony API server due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running telephony API server: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())