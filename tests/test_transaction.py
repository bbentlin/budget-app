import unittest
from decimal import Decimal

from budget_app.models.transaction import Transaction

class TestTransaction(unittest.TestCase):
  def test_from_input_success(self) -> None:
    tx = Transaction.from_input(
      raw_date="2024-01-15",
      raw_category="Groceries",
      raw_memo="Weekly shop",
      raw_amount="123.45",
    )
    self.assertEqual(tx.date.isoformat(), "2024-01-15")
    self.assertEqual(tx.category, "Groceries")
    self.assertEqual(tx.memo, "Weekly shop")
    self.assertEqual(tx.amount, Decimal("123.45"))

  def test_from_input_rejects_blank_category(self) -> None:
    with self.assertRaises(ValueError):
      Transaction.from_input(
        raw_date="2024-01-15",
        raw_category=" ",
        raw_memo="Anything",
        raw_amount="10.00",
      )

  def test_from_input_valid_amount(self) -> None:
    with self.assertRaises(ValueError):
      Transaction.from_input(
        raw_date="2024-01-15",
        raw_category="Utilities",
        raw_memo="Bill", 
        raw_amount="ten dollars",
      )