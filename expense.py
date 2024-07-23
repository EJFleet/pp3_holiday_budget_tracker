class Expense:
    def __init__(self, category, name, amount):
        self.category = category
        self.name = name
        self.amount = amount

    def __repr__(self):
        return f"Expense added: {self.name} for {self.amount:.2f} in {self.category}"
