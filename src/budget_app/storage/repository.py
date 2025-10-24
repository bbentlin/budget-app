class Repository:
    def __init__(self, storage_file='transactions.json'):
        self.storage_file = storage_file
        self.transactions = self.load_transactions()

    def load_transactions(self):
        try:
            with open(self.storage_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_transactions(self):
        with open(self.storage_file, 'w') as file:
            json.dump(self.transactions, file)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.save_transactions()

    def remove_transaction(self, transaction_id):
        self.transactions = [t for t in self.transactions if t['id'] != transaction_id]
        self.save_transactions()

    def get_all_transactions(self):
        return self.transactions

    def find_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction['id'] == transaction_id:
                return transaction
        return None