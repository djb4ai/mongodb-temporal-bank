import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MessageParser:
    """
    Parser for bank API responses.
    """
    
    def parse_balance_response(self, response_body: str) -> int:
        """
        Parse the response from a balance request.
        
        Args:
            response_body: The JSON response from the bank API
            
        Returns:
            The account balance
            
        Raises:
            ValueError: If the response is invalid or indicates an error
        """
        response = json.loads(response_body)
        
        if response.get("status") != "SUCCESS":
            error_message = response.get("message", "Unknown error")
            logger.error(f"Balance operation failed: {error_message}")
            
            if "No such bank" in error_message:
                from exceptions import NoSuchAccountException
                raise NoSuchAccountException(error_message)
            
            from exceptions import AccountOperationException
            raise AccountOperationException(error_message)
        
        return response.get("balance", 0)
    
    def parse_deposit_response(self, response_body: str) -> str:
        """
        Parse the response from a deposit request.
        
        Args:
            response_body: The JSON response from the bank API
            
        Returns:
            The transaction ID
            
        Raises:
            ValueError: If the response is invalid or indicates an error
        """
        response = json.loads(response_body)
        
        if response.get("status") != "SUCCESS":
            error_message = response.get("message", "Unknown error")
            logger.error(f"Deposit operation failed: {error_message}")
            
            if "No such bank" in error_message:
                from exceptions import NoSuchAccountException
                raise NoSuchAccountException(error_message)
            
            from exceptions import AccountOperationException
            raise AccountOperationException(error_message)
        
        return response.get("transaction-id", "")
    
    def parse_withdraw_response(self, response_body: str) -> str:
        """
        Parse the response from a withdraw request.
        
        Args:
            response_body: The JSON response from the bank API
            
        Returns:
            The transaction ID
            
        Raises:
            ValueError: If the response is invalid or indicates an error
            InsufficientFundsException: If the account has insufficient funds
        """
        response = json.loads(response_body)
        
        if response.get("status") != "SUCCESS":
            error_message = response.get("message", "Unknown error")
            logger.error(f"Withdrawal operation failed: {error_message}")
            
            if "No such bank" in error_message:
                from exceptions import NoSuchAccountException
                raise NoSuchAccountException(error_message)
            
            if "Insufficient funds" in error_message:
                from exceptions import InsufficientFundsException
                raise InsufficientFundsException(error_message)
            
            from exceptions import AccountOperationException
            raise AccountOperationException(error_message)
        
        return response.get("transaction-id", "")