class BudgetController:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def remove_transaction(self, transaction):
        if transaction in self.transactions:
            self.transactions.remove(transaction)

    def update_transaction(self, old_transaction, new_transaction):
        index = self.transactions.index(old_transaction) if old_transaction in self.transactions else -1
        if index != -1:
            self.transactions[index] = new_transaction

    def get_transactions(self):
        return self.transactions

    def calculate_total(self):
        return sum(transaction.amount for transaction in self.transactions)