from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Standardized transaction output format for all importers."""

    date: date
    description: str
    amount: Decimal
    opposing_account: str = Field(default="Cash Account")
