#!/usr/bin/env python3
"""
Script to run the SpeakWise telephony API server.
This starts the Flask server that handles incoming calls and webhooks.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.telephony.api import start_api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the SpeakWise telephony API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    
    args = parser.parse_args()
    
    logger.info(f"Starting telephony API server on {args.host}:{args.port}")
    
    try:
        # Start the API server
        start_api(host=args.host, port=args.port)
        return 0
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())