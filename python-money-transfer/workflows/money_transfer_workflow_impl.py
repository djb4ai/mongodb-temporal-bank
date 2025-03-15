import logging
import time
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

from models.transfer_details import TransferDetails
# Only import interface, not implementation
from workflows.money_transfer_workflow import MoneyTransferWorkflow
from exceptions import InsufficientFundsException

logger = logging.getLogger(__name__)

@workflow.defn
class MoneyTransferWorkflowImpl(MoneyTransferWorkflow):
    """
    Implementation of the money transfer workflow.
    """
    
    def __init__(self):
        """Initialize the workflow."""
        self.has_manager_approval = True  # Small transfers have approval by default
    
    @workflow.run
    async def transfer(self, input_details: TransferDetails) -> str:
        """
        Transfer money from one account to another.
        
        Args:
            input_details: Details of the transfer
            
        Returns:
            A confirmation string with transaction IDs
        """
        logger.info("Starting Money Transfer Workflow")
        
        # Large transfers must be explicitly approved by a manager
        if input_details.amount > 500:
            logger.warning("This transfer is on hold awaiting manager approval")
            self.has_manager_approval = False
        
        # The workflow blocks here awaiting approval, if that was required
        await workflow.wait_condition(lambda: self.has_manager_approval)
        
        # Set up retry options, similar to Java implementation
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            non_retryable_error_types=["exceptions.InsufficientFundsException"]
        )
        
        # Define activity options
        activity_options = {
            "schedule_to_close_timeout": timedelta(seconds=10),
            "retry_policy": retry_policy
        }
        
        # Withdraw money from sender's account
        logger.info("Starting withdraw operation")
        withdraw_key = f"withdrawal-for-{input_details.reference_id}"
        
        try:
            # Use string activity name instead of class reference
            withdraw_result = await workflow.execute_activity(
                "withdraw",  # Activity name as string
                args=[input_details.sender, input_details.amount, withdraw_key],
                **activity_options
            )
        except ApplicationError as e:
            if "InsufficientFundsException" in str(e):
                logger.error(f"Insufficient funds: {str(e)}")
                raise
            raise
        
        # Deposit money into recipient's account
        logger.info("Starting deposit operation")
        deposit_key = f"deposit-for-{input_details.reference_id}"
        
        # Use string activity name instead of class reference
        deposit_result = await workflow.execute_activity(
            "deposit",  # Activity name as string
            args=[input_details.recipient, input_details.amount, deposit_key],
            **activity_options
        )
        
        confirmation = f"withdrawal={withdraw_result}, deposit={deposit_result}"
        
        logger.info(f"Money Transfer Workflow now complete. Confirmation: {confirmation}")
        return confirmation
    
    @workflow.signal
    def approve(self, manager_name: str) -> None:
        """
        Approve a transfer that's waiting for manager approval.
        
        Args:
            manager_name: The name of the manager approving the transfer
        """
        logger.info(f"This transfer has now been approved by {manager_name}")
        self.has_manager_approval = True