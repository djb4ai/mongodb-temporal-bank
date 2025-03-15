import asyncio
import logging
import sys
import uuid

from temporalio.client import Client

from models.transfer_details import TransferDetails
from workflows.money_transfer_workflow_impl import MoneyTransferWorkflowImpl
from workers import TASK_QUEUE_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def start_workflow(sender: str, recipient: str, amount: int):
    """
    Start the money transfer workflow.
    
    Args:
        sender: The name of the sender's bank account
        recipient: The name of the recipient's bank account
        amount: The amount to transfer
    """
    # Generate a unique reference ID
    reference_id = str(uuid.uuid4())
    
    # Create transfer details
    details = TransferDetails(sender, recipient, amount, reference_id)
    
    logger.info(f"Will transfer {amount} from {sender} to {recipient}")
    
    # Create a workflow ID
    workflow_id = f"transfer-{amount}-{sender}-to-{recipient}".lower()
    
    # Connect to the Temporal server
    client = await Client.connect("localhost:7233")
    
    # Start the workflow
    handle = await client.start_workflow(
        MoneyTransferWorkflowImpl.transfer,
        details,
        id=workflow_id,
        task_queue=TASK_QUEUE_NAME
    )
    
    # Wait for the workflow to complete
    confirmation = await handle.result()
    
    logger.info(f"Money Transfer complete. Confirmation: {confirmation}")
    return confirmation

def validate_args():
    """
    Validate command-line arguments.
    
    Returns:
        Tuple of (sender, recipient, amount) if valid, None otherwise
    """
    if len(sys.argv) != 4:
        print("Incorrect number of arguments specified.")
        print("Format: SENDER RECIPIENT AMOUNT")
        return None
    
    sender = sys.argv[1]
    if not sender or not sender.strip():
        print("Sender name must not be empty")
        return None
    
    recipient = sys.argv[2]
    if not recipient or not recipient.strip():
        print("Recipient name must not be empty")
        return None
    
    try:
        amount = int(sys.argv[3])
    except ValueError:
        print(f"Could not parse specified amount: {sys.argv[3]}")
        return None
    
    return sender, recipient, amount

def main():
    """Main entry point for the starter application."""
    args = validate_args()
    if not args:
        sys.exit(1)
    
    sender, recipient, amount = args
    
    try:
        # Run the workflow
        asyncio.run(start_workflow(sender, recipient, amount))
    except KeyboardInterrupt:
        logger.info("Starter stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Starter failed with error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()