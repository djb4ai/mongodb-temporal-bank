import logging
import random
import string
import threading
from typing import Dict

from repository.bank_repository import BankRepository

logger = logging.getLogger(__name__)

class InsufficientFundsException(Exception):
    """Exception raised when a withdrawal would result in a negative balance."""
    pass

class Bank:
    """
    Represents a bank account with deposit and withdrawal functionality.
    """
    
    def __init__(self, name: str, repository: BankRepository):
        """
        Initialize a bank account.
        
        Args:
            name: The name of the bank account
            repository: The repository to use for persistence
        """
        logger.debug(f"Creating new bank named {name}")
        
        self.name = name
        self.repository = repository
        self._lock = threading.Lock()  # For thread safety
        self.requests: Dict[str, str] = {}
        
        account = repository.find_account_by_bank_name(name)
        if account is None:
            repository.create_account(name, 0)
            self.balance = 0
        else:
            self.balance = account.get("balance", 0)
    
    def get_name(self) -> str:
        """Get the name of the bank account."""
        return self.name
    
    def get_balance(self) -> int:
        """
        Get the current balance of the bank account.
        
        Returns:
            The current balance
        """
        with self._lock:
            return self.balance
    
    def deposit(self, amount: int, idempotency_key: str) -> str:
        """
        Deposit funds into the bank account.
        
        Args:
            amount: The amount to deposit
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            A transaction ID for the deposit
            
        Raises:
            ValueError: If the amount is less than 1
        """
        logger.info(f"Bank '{self.name}': deposit for {amount}, key is {idempotency_key}")
        
        if amount < 1:
            raise ValueError(f"Invalid deposit amount: {amount}")
        
        with self._lock:
            if idempotency_key in self.requests:
                return self.requests[idempotency_key]
            
            self.balance += amount
            tx_id = self._generate_transaction_id("D", 10)
            self.requests[idempotency_key] = tx_id
            
            self.repository.update_balance(self.name, self.balance)
            self.repository.log_transaction("deposit", amount, tx_id, idempotency_key, self.name)
            
            logger.debug(f"Bank '{self.name}': deposit complete for {amount}, txID is {tx_id}")
            return tx_id
    
    def withdraw(self, amount: int, idempotency_key: str) -> str:
        """
        Withdraw funds from the bank account.
        
        Args:
            amount: The amount to withdraw
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            A transaction ID for the withdrawal
            
        Raises:
            ValueError: If the amount is less than 1
            InsufficientFundsException: If the amount exceeds the balance
        """
        logger.info(f"Bank '{self.name}': withdraw for {amount}, key is {idempotency_key}")
        
        if amount < 1:
            raise ValueError(f"Invalid withdrawal amount: {amount}")
        
        with self._lock:
            if amount > self.balance:
                raise InsufficientFundsException(f"Insufficient funds: balance={self.balance}, withdrawal={amount}")
            
            if idempotency_key in self.requests:
                return self.requests[idempotency_key]
            
            self.balance -= amount
            tx_id = self._generate_transaction_id("W", 10)
            self.requests[idempotency_key] = tx_id
            
            self.repository.update_balance(self.name, self.balance)
            self.repository.log_transaction("withdraw", amount, tx_id, idempotency_key, self.name)
            
            logger.debug(f"Bank '{self.name}': withdraw complete for {amount}, txID is {tx_id}")
            return tx_id
    
    def _generate_transaction_id(self, prefix: str, length: int) -> str:
        """
        Generate a random transaction ID.
        
        Args:
            prefix: The prefix for the transaction ID
            length: The length of the random part of the ID
            
        Returns:
            A transaction ID
        """
        random_part = ''.join(random.choice(string.digits) for _ in range(length))
        return f"{prefix}{random_part}"