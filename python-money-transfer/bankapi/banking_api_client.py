import logging
import requests
import urllib.parse
from typing import Any, Dict

from .message_parser import MessageParser

logger = logging.getLogger(__name__)

class BankingApiClient:
    """
    Client for interacting with the bank API.
    """
    
    def __init__(self, hostname: str, port_number: int):
        """
        Initialize the client.
        
        Args:
            hostname: The hostname of the bank API server
            port_number: The port number of the bank API server
        """
        self.hostname = hostname
        self.port_number = port_number
        self.parser = MessageParser()
    
    def get_balance(self, bank_name: str) -> int:
        """
        Get the balance of a bank account.
        
        Args:
            bank_name: The name of the bank account
            
        Returns:
            The account balance
            
        Raises:
            NoSuchAccountException: If the account doesn't exist
            AccountOperationException: If the operation fails for another reason
            requests.RequestException: If the HTTP request fails
        """
        encoded_name = urllib.parse.quote(bank_name)
        url = f"http://{self.hostname}:{self.port_number}/api/balance?bankName={encoded_name}"
        
        response_body = self._call_service(url)
        balance = self.parser.parse_balance_response(response_body)
        
        return balance
    
    def deposit(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Deposit money into a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to deposit
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
            
        Raises:
            NoSuchAccountException: If the account doesn't exist
            AccountOperationException: If the operation fails for another reason
            requests.RequestException: If the HTTP request fails
        """
        encoded_name = urllib.parse.quote(bank_name)
        encoded_key = urllib.parse.quote(idempotency_key)
        
        url = f"http://{self.hostname}:{self.port_number}/api/deposit?bankName={encoded_name}" + \
              f"&amount={amount}&idempotencyKey={encoded_key}"
        
        response_body = self._call_service(url)
        transaction_id = self.parser.parse_deposit_response(response_body)
        
        return transaction_id
    
    def withdraw(self, bank_name: str, amount: int, idempotency_key: str) -> str:
        """
        Withdraw money from a bank account.
        
        Args:
            bank_name: The name of the bank account
            amount: The amount to withdraw
            idempotency_key: A key to ensure idempotency of the operation
            
        Returns:
            The transaction ID
            
        Raises:
            NoSuchAccountException: If the account doesn't exist
            InsufficientFundsException: If the account has insufficient funds
            AccountOperationException: If the operation fails for another reason
            requests.RequestException: If the HTTP request fails
        """
        encoded_name = urllib.parse.quote(bank_name)
        encoded_key = urllib.parse.quote(idempotency_key)
        
        url = f"http://{self.hostname}:{self.port_number}/api/withdraw?bankName={encoded_name}" + \
              f"&amount={amount}&idempotencyKey={encoded_key}"
        
        response_body = self._call_service(url)
        transaction_id = self.parser.parse_withdraw_response(response_body)
        
        return transaction_id
    
    def _call_service(self, service_url: str) -> str:
        """
        Make an HTTP request to the bank API.
        
        Args:
            service_url: The URL to call
            
        Returns:
            The response body as a string
            
        Raises:
            requests.RequestException: If the HTTP request fails
        """
        logger.debug(f"Making call to URL {service_url}")
        
        response = requests.get(service_url, timeout=10)
        response.raise_for_status()
        
        return response.text