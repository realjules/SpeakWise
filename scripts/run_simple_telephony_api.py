#!/usr/bin/env python3
"""
Script to run the simplified SpeakWise telephony API server.
This version doesn't depend on Flask.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the project root to the path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.integrations.telephony.simple_api import start_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the simplified telephony API server"""
    parser = argparse.ArgumentParser(description="Run the SpeakWise simplified telephony API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--api-key", required=True, help="Pindo API key")
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting simplified telephony API server on {args.host}:{args.port}")
        start_api(host=args.host, port=args.port, api_key=args.api_key)
    except KeyboardInterrupt:
        logger.info("Shutting down telephony API server due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running telephony API server: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())