import logging
from typing import Dict, List, Optional

from bank import Bank
from repository.bank_repository import BankRepository

logger = logging.getLogger(__name__)

class BankManager:
    """
    Manages a collection of bank accounts.
    """
    
    def __init__(self, repository: BankRepository):
        """
        Initialize the bank manager.
        
        Args:
            repository: The repository to use for persistence
        """
        self.repository = repository
        self.banks: Dict[str, Bank] = {}
        self._load_banks()
    
    def _load_banks(self) -> None:
        """Load all banks from the repository."""
        logger.debug("Loading all banks from repository")
        banks = self.repository.get_all_banks()
        for bank_doc in banks:
            bank_name = bank_doc.get("bankName")
            if bank_name:
                self.banks[bank_name] = Bank(bank_name, self.repository)
    
    def get_bank(self, bank_name: str) -> Optional[Bank]:
        """
        Get a bank by name, creating it if it doesn't exist.
        
        Args:
            bank_name: The name of the bank to get
            
        Returns:
            The bank object or None if it doesn't exist
        """
        if bank_name not in self.banks:
            # Check if it exists in the repository
            account = self.repository.find_account_by_bank_name(bank_name)
            if account:
                # Create the bank object for an existing account
                self.banks[bank_name] = Bank(bank_name, self.repository)
            else:
                return None
        
        return self.banks.get(bank_name)
    
    def create_bank(self, bank_name: str, initial_balance: int = 0) -> Bank:
        """
        Create a new bank.
        
        Args:
            bank_name: The name of the new bank
            initial_balance: The initial balance for the bank
            
        Returns:
            The newly created bank
        """
        logger.info(f"Creating new bank: {bank_name} with initial balance: {initial_balance}")
        
        # Check if bank already exists
        if bank_name in self.banks:
            return self.banks[bank_name]
        
        # Create new bank in the repository
        self.repository.create_account(bank_name, initial_balance)
        
        # Create the bank object
        bank = Bank(bank_name, self.repository)
        self.banks[bank_name] = bank
        
        return bank
    
    def get_all_banks(self) -> List[Bank]:
        """
        Get all banks.
        
        Returns:
            A list of all bank objects
        """
        # Refresh from repository to catch any new banks
        self._load_banks()
        return list(self.banks.values())
    
    def get_bank_status(self, bank_name: str) -> Optional[str]:
        """
        Get the status of a bank.
        
        Args:
            bank_name: The name of the bank
            
        Returns:
            The status of the bank or None if the bank doesn't exist
        """
        bank_doc = self.repository.find_account_by_bank_name(bank_name)
        if bank_doc:
            return bank_doc.get("status", "ACTIVE")
        return None
    
    def set_bank_status(self, bank_name: str, status: str) -> bool:
        """
        Set the status of a bank.
        
        Args:
            bank_name: The name of the bank
            status: The new status ('ACTIVE' or 'STOPPED')
            
        Returns:
            True if the status was updated, False otherwise
        """
        if bank_name not in self.banks:
            return False
        
        if status not in ["ACTIVE", "STOPPED"]:
            raise ValueError(f"Invalid bank status: {status}")
        
        logger.info(f"Setting bank {bank_name} status to {status}")
        self.repository.update_bank_status(bank_name, status)
        return True