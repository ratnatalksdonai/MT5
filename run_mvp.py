#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  ██████╗  █████╗ ████████╗███╗   ██╗ █████╗     ██╗  ██╗██╗██████╗ ████████╗██╗ ║
║  ██╔══██╗██╔══██╗╚══██╔══╝████╗  ██║██╔══██╗    ██║ ██╔╝██║██╔══██╗╚══██╔══╝██║ ║
║  ██████╔╝███████║   ██║   ██╔██╗ ██║███████║    █████╔╝ ██║██████╔╝   ██║   ██║ ║
║  ██╔══██╗██╔══██║   ██║   ██║╚██╗██║██╔══██║    ██╔═██╗ ██║██╔══██╗   ██║   ██║ ║
║  ██║  ██║██║  ██║   ██║   ██║ ╚████║██║  ██║    ██║  ██╗██║██║  ██║   ██║   ██║ ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ║
║                                                                               ║
║           🚀 PROFESSIONAL MT5-MATCHTRADER BRIDGE v1.0 🚀                     ║
║                                                                               ║
║                    Engineered by Ratna Kirti (@ratna3)                       ║
║                   Professional Software Engineer                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Enterprise-Grade Trade Replication System
• Real-time MT5 position monitoring
• Secure MatchTrader API integration
• Multi-account support with failover
• Professional logging and error handling

Usage: python run_mvp.py
Author: Ratna Kirti (https://github.com/ratna3)
License: MIT
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from src.trade_copier_mvp import TradeCopierMVP

def setup_logging():
    """Setup logging configuration"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "trade_copier.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Check if config file exists (try private first, then regular)
        config_paths = [
            "config/config_mvp.private.json",
            "config/config_mvp.json", 
            "config_mvp.private.json",  # Legacy location
            "config_mvp.json"           # Legacy location
        ]
        
        config_file = None
        for path in config_paths:
            if os.path.exists(path):
                config_file = path
                break
                
        if not config_file:
            logger.error("Configuration file not found!")
            logger.info("Please create config/config_mvp.private.json with your account details.")
            logger.info("Use config/config_mvp.sample.json as a template.")
            sys.exit(1)
        
        copier = TradeCopierMVP(config_file)
        
        # Setup signal handlers for graceful shutdown
        shutdown_event = asyncio.Event()
        
        def signal_handler(sig, frame):
            logger.info("\nShutdown signal received. Stopping trade copier...")
            shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the trade copier
        logger.info("Starting MT5 to MatchTrader MVP...")
        
        # Run until shutdown signal
        copy_task = asyncio.create_task(copier.start_copying())
        shutdown_task = asyncio.create_task(shutdown_event.wait())
        
        done, pending = await asyncio.wait(
            [copy_task, shutdown_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        await copier.stop_copying()
        logger.info("Trade copier stopped gracefully.")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please check your config_mvp.json file.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full error details:")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Failed to start: {e}")
        sys.exit(1)
