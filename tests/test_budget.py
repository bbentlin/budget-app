import unittest
from src.budget_app.controllers.budget_controller import BudgetController
from src.budget_app.models.transaction import Transaction

class TestBudgetController(unittest.TestCase):

    def setUp(self):
        self.controller = BudgetController()

    def test_add_transaction(self):
        transaction = Transaction(amount=100, date='2023-01-01', category='Food')
        self.controller.add_transaction(transaction)
        self.assertIn(transaction, self.controller.transactions)

    def test_remove_transaction(self):
        transaction = Transaction(amount=50, date='2023-01-02', category='Transport')
        self.controller.add_transaction(transaction)
        self.controller.remove_transaction(transaction)
        self.assertNotIn(transaction, self.controller.transactions)

    def test_update_transaction(self):
        transaction = Transaction(amount=200, date='2023-01-03', category='Entertainment')
        self.controller.add_transaction(transaction)
        updated_transaction = Transaction(amount=250, date='2023-01-03', category='Entertainment')
        self.controller.update_transaction(transaction, updated_transaction)
        self.assertIn(updated_transaction, self.controller.transactions)
        self.assertNotIn(transaction, self.controller.transactions)

if __name__ == '__main__':
    unittest.main()