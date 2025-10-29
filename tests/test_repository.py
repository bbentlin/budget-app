import json
import tempfile
import unittest
from pathlib import Path

from budget_app.models.transaction import Transaction
from budget_app.storage.repository import TransactionRepository

class TestTransactionRepository(unittest.TestCase):
  def test_round_trip(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "transactions.json" 
      repo = TransactionRepository(path)

      original = [
        Transaction.from_input(
          raw_date="2024-05-01",
          raw_category="Salary",
          raw_memo="Monthly pay",
          raw_amount="3500.00",
        ),
        Transaction.from_input(
          raw_date="2024-05-02",
          raw_category="Rent",
          raw_memo="May Rent",
          raw_amount="-1200.00",
        ),
      ]

      repo.save(original)
      loaded = repo.load()

      self.assertEqual(original, loaded)

  def test_load_with_invalid_payload(self) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / "transactions.json"
      path.write_text(json.dumps([{"date": "bad"}]), encoding="utf-8")

      repo = TransactionRepository(path)
      self.assertEqual(repo.load(), [])