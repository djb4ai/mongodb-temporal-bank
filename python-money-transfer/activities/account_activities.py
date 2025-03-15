import logging
from abc import ABC, abstractmethod

from temporalio import activity

from exceptions import InsufficientFundsException
from bankapi.banking_api_client import BankingApiClient

logger = logging.getLogger(__name__)


class AccountActivities(ABC):
    """
    Interface for account activities.
    """
    
    @abstractmethod
    def deposit(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Deposit money into a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to deposit
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
        """
        pass
    
    @abstractmethod
    def withdraw(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Withdraw money from a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to withdraw
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
        """
        pass

class AccountActivitiesImpl(AccountActivities):
    """
    Implementation of account activities.
    """
    
    def __init__(self, hostname: str = "localhost", port: int = 8480):
        """
        Initialize the activities with a bank API client.
        
        Args:
            hostname: The hostname of the bank API server
            port: The port number of the bank API server
        """
        self.client = BankingApiClient(hostname, port)
    
    @activity.defn(name="deposit")
    def deposit(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Deposit money into a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to deposit
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
        """
        logger.info(f"Depositing {amount} into account {bank_name} with key {idempotency_key}")
        return self.client.deposit(bank_name, amount, idempotency_key)
    
    @activity.defn(name="withdraw")
    def withdraw(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Withdraw money from a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to withdraw
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
        """
        logger.info(f"Withdrawing {amount} from account {bank_name} with key {idempotency_key}")
        try:
            return self.client.withdraw(bank_name, amount, idempotency_key)
        except InsufficientFundsException as e:
            # Re-raise to maintain the exception type
            logger.error(f"Insufficient funds: {str(e)}")
            raise