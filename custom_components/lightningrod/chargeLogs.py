import json
import asyncio
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging to show debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the parent directory to Python path so we can import fordpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fordpass.fordpass_new import Vehicle

# Handle imports for both module and direct script usage
if __package__ is None:
    # Running as script
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir))
    from myconfig import fp_username, fp_password, fp_vin, fp_token
else:
    # Running as module
    from .myconfig import fp_username, fp_password, fp_vin, fp_token

_LOGGER = logging.getLogger(__name__)

async def main():
    _LOGGER.debug("Starting charge log retrieval")
    
    # Setup paths
    current_dir = Path(__file__).parent
    token_path = current_dir.parent / "fordpass" / f"{fp_username}_fordpass_token.txt"
    output_file = current_dir / "ChargeLogs.json"
    
    _LOGGER.debug(f"Using token path: {token_path}")
    
    # Initialize vehicle with credentials from config
    vehicle = Vehicle(
        username=fp_username,
        password=fp_password,
        vin=fp_vin,
        region="USA",  # Default to USA region
        save_token=False,
        config_location=str(token_path)
    )

    try:
        # Get charge logs
        _LOGGER.debug("Requesting charge logs from vehicle")
        logs = await vehicle.ev_energy_transfer_logs()
        
        if not logs:
            _LOGGER.warning("No charge logs retrieved")
            return

        # Save to JSON file
        with open(output_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        _LOGGER.info(f"Successfully saved charge logs to {output_file}")

    except Exception as e:
        _LOGGER.error(f"Error getting charge logs: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())

