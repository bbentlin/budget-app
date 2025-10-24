class Transaction:
    def __init__(self, amount, date, category):
        self.amount = amount
        self.date = date
        self.category = category

    def __repr__(self):
        return f"Transaction(amount={self.amount}, date={self.date}, category='{self.category}')"