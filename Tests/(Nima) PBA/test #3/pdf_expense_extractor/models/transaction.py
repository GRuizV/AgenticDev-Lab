"""
Transaction data model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Represents a credit card transaction."""
    
    date: str  # ISO format: YYYY-MM-DD
    description: str
    amount: float  # Amount in pesos
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not self.date:
            raise ValueError("Transaction date cannot be empty")
        
        if not self.description:
            raise ValueError("Transaction description cannot be empty")
        
        if self.amount < 0:
            raise ValueError("Transaction amount cannot be negative")
        
        # Validate date format
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {self.date}. Expected YYYY-MM-DD")
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            'date': self.date,
            'description': self.description,
            'amount': self.amount
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            date=data['date'],
            description=data['description'],
            amount=data['amount']
        )
    
    def __str__(self) -> str:
        """String representation of transaction."""
        return f"{self.date} | {self.description} | ${self.amount:,.2f}"