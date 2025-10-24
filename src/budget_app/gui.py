from tkinter import Tk, Label, Button, Entry, StringVar, Frame, messagebox

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Application")
        self.root.geometry("400x300")

        self.amount_var = StringVar()
        self.category_var = StringVar()

        self.create_widgets()

    def create_widgets(self):
        frame = Frame(self.root)
        frame.pack(pady=10)

        Label(frame, text="Amount:").grid(row=0, column=0)
        Entry(frame, textvariable=self.amount_var).grid(row=0, column=1)

        Label(frame, text="Category:").grid(row=1, column=0)
        Entry(frame, textvariable=self.category_var).grid(row=1, column=1)

        Button(frame, text="Add Transaction", command=self.add_transaction).grid(row=2, columnspan=2)

    def add_transaction(self):
        amount = self.amount_var.get()
        category = self.category_var.get()

        if not amount or not category:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        # Here you would typically call the controller to handle the transaction
        messagebox.showinfo("Success", f"Transaction added: {amount} in {category}")

if __name__ == "__main__":
    root = Tk()
    app = BudgetApp(root)
    root.mainloop()