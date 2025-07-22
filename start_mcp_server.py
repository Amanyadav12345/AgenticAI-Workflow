#!/usr/bin/env python3
"""
Start the MCP Server for Agentic AI Workflow Tools
"""

import asyncio
import sys
import argparse
from mcp_server import main as mcp_main
from utils.logger import setup_logger

def main():
    """Main entry point for MCP server"""
    parser = argparse.ArgumentParser(description="Agentic AI Workflow MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        import os
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    logger = setup_logger("mcp_server_main")
    
    logger.info("🤖 Starting Agentic AI Workflow MCP Server...")
    logger.info("This server provides workflow automation tools via MCP protocol")
    
    try:
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        logger.info("👋 MCP Server stopped by user")
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()