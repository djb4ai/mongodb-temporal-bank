import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio import activity

from activities.account_activities import AccountActivitiesImpl
from workflows.money_transfer_workflow_impl import MoneyTransferWorkflowImpl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Task queue name
TASK_QUEUE_NAME = "MoneyTransferTaskQueue"

# Shutdown flag
shutdown = False

# Signal handler for graceful shutdown
def handle_signal(signum, frame):
    global shutdown
    logger.info(f"Received signal {signum}, initiating shutdown")
    shutdown = True

async def run_worker():
    """Start and run the worker."""
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create an instance of the AccountActivitiesImpl class
    account_activities = AccountActivitiesImpl(hostname="localhost", port=8480)
    
    # Create a thread pool executor for synchronous activities
    activity_executor = ThreadPoolExecutor(max_workers=10)
    
    # Create a worker that hosts the workflow implementation and activities
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[MoneyTransferWorkflowImpl],
        # Register the activities
        activities=[
            account_activities.deposit,
            account_activities.withdraw
        ],
        activity_executor=activity_executor
    )
    
    # Start the worker
    logger.info(f"Starting worker, connecting to task queue '{TASK_QUEUE_NAME}'")
    
    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, handle_signal)
    
    # Start the worker
    async with worker:
        # Keep the worker running until shutdown is requested
        while not shutdown:
            await asyncio.sleep(0.5)
    
    logger.info("Worker shutdown complete")

def main():
    """Main entry point for the worker application."""
    try:
        # Run the worker
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Worker failed with error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()