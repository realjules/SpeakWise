#!/usr/bin/env python
"""
Script to run the browser agent for Irembo services.

This script provides a command-line interface to run the browser agent
for different Irembo services, with optional SMS notifications and
dashboard updates.
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add the project root to the path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the browser agent
from src.browser_agent.browser_agent import BrowserUseAgent


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run browser agent for Irembo services')
    
    parser.add_argument('--service', type=str, choices=['birth_certificate', 'driving_license'], 
                        default='birth_certificate', help='Service to access')
    
    parser.add_argument('--for-self', action='store_true', default=True,
                        help='Whether the birth certificate is for self (default: True)')
    
    parser.add_argument('--district', type=str, default='Gasabo',
                        help='District for processing office')
    
    parser.add_argument('--sector', type=str, default='Jali',
                        help='Sector for processing office')
    
    parser.add_argument('--reason', type=str, default='Education',
                        help='Reason for application')
    
    parser.add_argument('--test-type', type=str, 
                        default='Registration for Driving Test - Provisional, paper-based',
                        help='Type of driving test')
    
    parser.add_argument('--headless', action='store_true', default=False,
                        help='Run in headless mode')
    
    parser.add_argument('--model', type=str, default='gpt-4o',
                        help='LLM model to use')
    
    parser.add_argument('--verbose', action='store_true', default=True,
                        help='Enable verbose output')
    
    parser.add_argument('--disable-sms', action='store_true', default=False,
                        help='Disable SMS notifications')
    
    parser.add_argument('--disable-dashboard', action='store_true', default=False,
                        help='Disable dashboard updates')
    
    return parser.parse_args()


def main():
    """Run the browser agent with the specified arguments."""
    args = parse_args()
    
    try:
        # Create the agent with SMS and dashboard options
        agent = BrowserUseAgent(
            model=args.model,
            verbose=args.verbose,
            headless=args.headless,
            sms_enabled=not args.disable_sms,
            update_dashboard=not args.disable_dashboard
        )
        
        # Print service information
        print(f"Starting service: {args.service}")
        print(f"SMS notifications: {'Disabled' if args.disable_sms else 'Enabled'}")
        print(f"Dashboard updates: {'Disabled' if args.disable_dashboard else 'Enabled'}")
        
        # Run the appropriate service
        if args.service == 'birth_certificate':
            result = agent.run_async(
                agent.apply_for_birth_certificate(
                    for_self=args.for_self,
                    processing_office={"District": args.district, "Sector": args.sector},
                    reason=args.reason
                )
            )
            service_name = "Birth Certificate"
            
        elif args.service == 'driving_license':
            result = agent.run_async(
                agent.register_driving_license_exam(
                    test_type=args.test_type,
                    district=args.district
                )
            )
            service_name = "Driving License Exam Registration"
        
        # Print completion message with formatted results
        print(f"\n{service_name} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Status: {result.get('status', 'unknown')}")
        
        # If SMS was enabled, show notification details
        if not args.disable_sms:
            print("\nSMS notification sent to: " + agent.phone_number)
        
        # If dashboard updates were enabled, show update details
        if not args.disable_dashboard:
            print("\nDashboard updated with new transaction data")
        
        # Return success
        return 0
        
    except Exception as e:
        print(f"Error running browser agent: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())