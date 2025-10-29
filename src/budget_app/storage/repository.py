from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable

from budget_app.models.transaction import Transaction

class TransactionRepository:
  def __init__(self, path: Path) -> None:
    self._path = path

  def load(self) -> list[Transaction]:
    if not self._path.exists():
      return []
    try:
      payload = json.loads(self._path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
      return []
    
    transactions: list[Transaction] = []
    for item in payload:
      try:
        transactions.append(
          Transaction(
            date=date.fromisoformat(item["date"]),
            category=item["category"],
            memo=item.get("memo", ""),
            amount=Decimal(item["amount"]),
          )
        )
      except (KeyError, ValueError, InvalidOperation):
        continue
    return transactions
  
  def save(self, transactions: Iterable[Transaction]) -> None:
    serializable = [
      {
        "date": tx.date.isoformat(),
        "category": tx.category,
        "memo": tx.memo,
        "amount": format(tx.amount, "f"),
      }
      for tx in transactions
    ]
    self._path.parent.mkdir(parents=True, exist_ok=True)
    self._path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")