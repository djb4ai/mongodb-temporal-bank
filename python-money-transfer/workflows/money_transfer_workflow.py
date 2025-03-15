from abc import ABC, abstractmethod
from models.transfer_details import TransferDetails

class MoneyTransferWorkflow(ABC):
    """
    Interface for the money transfer workflow.
    """
    
    @abstractmethod
    def transfer(self, input_details: TransferDetails) -> str:
        """
        Transfer money from one account to another.
        
        Args:
            input_details: Details of the transfer
            
        Returns:
            A confirmation string with transaction IDs
        """
        pass
    
    @abstractmethod
    def approve(self, manager_name: str) -> None:
        """
        Approve a transfer that's waiting for manager approval.
        
        Args:
            manager_name: The name of the manager approving the transfer
        """
        pass