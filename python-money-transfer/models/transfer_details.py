from dataclasses import dataclass

@dataclass
class TransferDetails:
    """
    Details for a money transfer.
    
    Attributes:
        sender: The name of the sender's bank account
        recipient: The name of the recipient's bank account
        amount: The amount to transfer
        reference_id: A unique reference ID for the transfer
    """
    sender: str
    recipient: str
    amount: int
    reference_id: str