import os
import logging
import sys
from dotenv import load_dotenv

from config.mongodb_config import MongodbConfig
from repository.bank_repository_impl import BankRepositoryImpl
from bank_manager import BankManager
from bank_controller import BankController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Default port
SERVICE_PORT = 8481

def main():
    """Main entry point for the application."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    try:
        logger.info("Starting application")
        
        if os.getenv(MongodbConfig.CONN_STRING_ENV_VARNAME) is None:
            logger.error(f"{MongodbConfig.CONN_STRING_ENV_VARNAME} environment variable is not set!")
            sys.exit(1)
        
        logger.debug("Setting up MongoDB connection")
        database = MongodbConfig.get_database()
        repository = BankRepositoryImpl(database)
        
        logger.debug("Initializing BankManager")
        manager = BankManager(repository)
        
        logger.debug("Starting the server")
        controller = BankController(manager, SERVICE_PORT)
        
        # Check for --no-web argument
        no_web = "--no-web" in sys.argv
        
        if no_web:
            logger.info("Web UI disabled")
            
        controller.start()
            
    except Exception as e:
        logger.error(f"Error encountered while running the application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
