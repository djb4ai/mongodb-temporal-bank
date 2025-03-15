from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BankRepository(ABC):
    """
    Abstract interface for bank repository operations.
    """
    
    @abstractmethod
    def find_account_by_bank_name(self, bank_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a bank account by name.
        
        Args:
            bank_name: The name of the bank account to find
            
        Returns:
            The account document or None if not found
        """
        pass
    
    @abstractmethod
    def create_account(self, bank_name: str, initial_balance: int) -> None:
        """
        Create a new bank account.
        
        Args:
            bank_name: The name of the new bank account
            initial_balance: The initial balance for the account
        """
        pass
    
    @abstractmethod
    def update_balance(self, bank_name: str, new_balance: int) -> None:
        """
        Update the balance of a bank account.
        
        Args:
            bank_name: The name of the bank account to update
            new_balance: The new balance for the account
        """
        pass
    
    @abstractmethod
    def log_transaction(self, operation: str, amount: int, tx_id: str, idempotency_key: str, bank_name: str) -> None:
        """
        Log a transaction.
        
        Args:
            operation: The type of operation (deposit, withdraw)
            amount: The amount involved in the transaction
            tx_id: The transaction ID
            idempotency_key: The idempotency key for the transaction
            bank_name: The name of the bank account involved
        """
        pass
    
    @abstractmethod
    def get_all_banks(self) -> list:
        """
        Get all banks.
        
        Returns:
            A list of all bank accounts
        """
        pass