import unittest
from decimal import Decimal

from budget_app.models.transaction import Transaction


class TestTransaction(unittest.TestCase):
    def test_from_input_income_success(self) -> None:
        tx = Transaction.from_input(
            raw_date="2024-01-15",
            raw_category="Groceries",
            raw_memo="Weekly shop",
            raw_amount="123.45",
            raw_kind="income",
        )
        self.assertEqual(tx.amount, Decimal("123.45"))

    def test_from_input_expense_negates_amount(self) -> None:
        tx = Transaction.from_input(
            raw_date="2024-01-15",
            raw_category="Dining",
            raw_memo="Dinner out",
            raw_amount="45.00",
            raw_kind="expense",
        )
        self.assertEqual(tx.amount, Decimal("-45.00"))

    def test_from_input_rejects_blank_category(self) -> None:
        with self.assertRaises(ValueError):
            Transaction.from_input(
                raw_date="2024-01-15",
                raw_category=" ",
                raw_memo="Anything",
                raw_amount="10.00",
                raw_kind="income",
            )

    def test_from_input_invalid_kind(self) -> None:
        with self.assertRaises(ValueError):
            Transaction.from_input(
                raw_date="2024-01-15",
                raw_category="Misc",
                raw_memo="Unknown",
                raw_amount="5.00",
                raw_kind="bonus",
            )

    def test_from_input_invalid_amount(self) -> None:
        with self.assertRaises(ValueError):
            Transaction.from_input(
                raw_date="2024-01-15",
                raw_category="Utilities",
                raw_memo="Bill",
                raw_amount="ten dollars",
                raw_kind="income",
            )