#!/usr/bin/env python3
"""
MT5 to MatchTrader MVP Runner
Usage: python run_mvp.py
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
        # Check if config file exists
        if not os.path.exists("config_mvp.json"):
            logger.error("Configuration file 'config_mvp.json' not found!")
            logger.info("Please create the config file with your account details.")
            sys.exit(1)
        
        copier = TradeCopierMVP("config_mvp.json")
        
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
