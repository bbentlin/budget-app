from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Self

@dataclass(slots=True, frozen=True)
class Transaction:
  date: date
  category: str
  memo: str 
  amount: Decimal 

  @classmethod
  def from_input(cls, *, raw_date: str, raw_category: str, raw_memo: str, raw_amount: str) -> Self:
    from datetime import date as _date
    from decimal import Decimal, InvalidOperation

    category = raw_category.strip()
    memo = raw_memo.strip()

    if not category:
      raise ValueError("Category cannot be empty.")
    
    try:
      parsed_date = date.fromisoformat(raw_date.strip())
    except ValueError as exc:
      raise ValueError("Use YYYY-MM-DD format.") from exc
    
    try: 
      parsed_amount = Decimal(raw_amount.strip())
    except (InvalidOperation, ValueError) as exc:
      raise ValueError("Enter a valid numeric amount.")
    
    return cls(date=parsed_date, category=category, memo=memo, amount=parsed_amount)