import logging
from typing import Dict, Any, Optional
from pymongo.database import Database
from datetime import datetime

from .bank_repository import BankRepository

logger = logging.getLogger(__name__)

class BankRepositoryImpl(BankRepository):
    """
    MongoDB implementation of the BankRepository interface.
    """
    
    def __init__(self, database: Database):
        """
        Initialize the repository with a MongoDB database.
        
        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.accounts_collection = database["accounts"]
        self.transactions_collection = database["transactions"]
        
        # Create indexes if they don't exist
        self.accounts_collection.create_index("bankName", unique=True)
    
    def find_account_by_bank_name(self, bank_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a bank account by name.
        
        Args:
            bank_name: The name of the bank account to find
            
        Returns:
            The account document or None if not found
        """
        return self.accounts_collection.find_one({"bankName": bank_name})
    
    def create_account(self, bank_name: str, initial_balance: int) -> None:
        """
        Create a new bank account.
        
        Args:
            bank_name: The name of the new bank account
            initial_balance: The initial balance for the account
        """
        logger.info(f"Creating account for {bank_name} with initial balance {initial_balance}")
        self.accounts_collection.insert_one({
            "bankName": bank_name,
            "balance": initial_balance,
            "status": "ACTIVE",
            "created": datetime.now()
        })
    
    def update_balance(self, bank_name: str, new_balance: int) -> None:
        """
        Update the balance of a bank account.
        
        Args:
            bank_name: The name of the bank account to update
            new_balance: The new balance for the account
        """
        logger.debug(f"Updating balance for {bank_name} to {new_balance}")
        self.accounts_collection.update_one(
            {"bankName": bank_name},
            {"$set": {"balance": new_balance}}
        )
    
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
        logger.info(f"Logging transaction: {operation} {amount} for {bank_name}, txID: {tx_id}")
        self.transactions_collection.insert_one({
            "operation": operation,
            "amount": amount,
            "txId": tx_id,
            "idempotencyKey": idempotency_key,
            "bankName": bank_name,
            "timestamp": datetime.now()
        })
    
    def get_all_banks(self) -> list:
        """
        Get all banks.
        
        Returns:
            A list of all bank accounts
        """
        return list(self.accounts_collection.find({}))
        
    def update_bank_status(self, bank_name: str, status: str) -> None:
        """
        Update the status of a bank account.
        
        Args:
            bank_name: The name of the bank account to update
            status: The new status for the account ('ACTIVE' or 'STOPPED')
        """
        logger.info(f"Updating status for {bank_name} to {status}")
        self.accounts_collection.update_one(
            {"bankName": bank_name},
            {"$set": {"status": status}}
        )