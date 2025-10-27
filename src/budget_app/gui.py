import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

class BudgetApp:
  def __init__(self) -> None:
    self.root = tk.Tk()
    self.root.title("Budget App")
    self.root.geometry("800x520")
    self.root.minsize(720, 440)

    self.transactions: list[dict] = []

    self._summary_vars: dict[str, tk.StringVar] = {
      "balance": tk.StringVar(value="$0.00"),
      "income": tk.StringVar(value="$0.00"),
      "expenses": tk.StringVar(value="$0.00"),
    }

    self._amount_var = tk.StringVar()
    self._category_var = tk.StringVar()
    self._memo_var = tk.StringVar()
    self._date_var = tk.StringVar(value=date.today().isoformat())

    self._configure_style()
    self._build_menu()
    self._build_layout()

  def run(self) -> None:
    self.root.mainloop()

  def _configure_style(self) -> None:
    style = ttk.Style(self.root)
    style.theme_use("clam")
    style.configure("Summary.TLabel", font=("Helvetica Neue", 14, "bold"))
    style.configure("SummaryValue.TLabel", font=("Helvetica Neue", 16))

  def _build_menu(self) -> None:
    menu_bar = tk.Menu(self.root)
    file_menu = tk.Menu(menu_bar, tearoff=False)
    file_menu.add_command(label="Export CSV…", command=self._on_export_csv)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=self.root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    self.root.config(menu=menu_bar)

  def _build_layout(self) -> None:
    container = ttk.Frame(self.root, padding=16)
    container.pack(fill="both", expand=True)

    summary_frame = ttk.Frame(container)
    summary_frame.pack(fill="x", pady=(0, 16))
    for idx, (label, var) in enumerate(self._summary_vars.items()):
      block = ttk.Frame(summary_frame, padding=12)
      block.grid(row=0, column=idx, sticky="nsew", padx=8)
      summary_frame.columnconfigure(idx, weight=1)
      ttk.Label(block, text=label.title(), style="Summary.TLabel").pack(anchor="w")
      ttk.Label(block, textvariable=var, style="SummaryValue.TLabel").pack(anchor="w")

    tree_frame = ttk.LabelFrame(container, text="Transactions")
    tree_frame.pack(fill="both", expand=True, pady=(0, 16))

    columns = ("date", "category", "memo", "amount")
    self._tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    self._tree.heading("date", text="Date")
    self._tree.heading("category", text="Category")
    self._tree.heading("memo", text="Memo")
    self._tree.heading("amount", text="Amount")
    self._tree.column("date", width=90, anchor="center")
    self._tree.column("category", width=120)
    self._tree.column("memo", width=260)
    self._tree.column("amount", width=100, anchor="e")
    self._tree.pack(fill="both", expand=True, side="left", padx=(8, 0), pady=8)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
    scrollbar.pack(fill="y", side="right", padx=(0, 8), pady=8)
    self._tree.configure(yscrollcommand=scrollbar.set)

    tree_actions = ttk.Frame(tree_frame)
    tree_actions.pack(fill="x", side="bottom", anchor="e", padx=8, pady=(0, 8))
    ttk.Button(tree_actions, text="Delete Selected", command=self._on_delete_selected).pack(anchor="e")

    form = ttk.LabelFrame(container, text="Add Transaction", padding=12)
    form.pack(fill="x")

    ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
    ttk.Entry(form, textvariable=self._date_var, width=18).grid(row=1, column=0, sticky="w")

    ttk.Label(form, text="Category").grid(row=0, column=1, sticky="w", padx=(12, 0))
    ttk.Entry(form, textvariable=self._category_var, width=18).grid(row=1, column=1, sticky="w", padx=(12, 0))

    ttk.Label(form, text="Memo").grid(row=0, column=2, sticky="w", padx=(12, 0))
    ttk.Entry(form, textvariable=self._memo_var, width=30).grid(row=1, column=2, sticky="w", padx=(12, 0))

    ttk.Label(form, text="Amount").grid(row=0, column=3, sticky="w", padx=(12, 0))
    ttk.Entry(form, textvariable=self._amount_var, width=14).grid(row=1, column=3, sticky="w", padx=(12, 0))

    ttk.Button(form, text="Add", command=self._on_add_transaction).grid(
      row=1, 
      column=4, 
      padx=(18, 0),
    )

    for col in range(5):
      form.columnconfigure(col, weight=1 if col in (2,) else 0)

  def _on_add_transaction(self) -> None:
    try:
      amount = Decimal(self._amount_var.get().strip())
    except (InvalidOperation, ValueError):
      messagebox.showerror("Invalid Amount", "Enter a valid numeric amount.")
      return
    
    try:
      tx_date = date.fromisoformat(self._date_var.get().strip())
    except ValueError:
      messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format.")
      return

    category = self._category_var.get().strip()
    memo = self._memo_var.get().strip()

    if not category:
      messagebox.showwarning("Missing Category", "Category cannot be empty.")
      return

    transaction = {
      "date": tx_date,
      "category": category,
      "memo": memo,
      "amount": amount,
    }
    self.transactions.append(transaction)
    self._refresh_tree()
    self._update_summary()
    self._reset_form()

  def _on_delete_selected(self) -> None:
    selected = self._tree.selection()
    if not selected:
      messagebox.showinfo("Delete Transaction", "Select at least one transaction to delete.")
      return 
    for item_id in selected:
      index = int(self._tree.item(item_id, "text"))
      if 0 <= index < len(self.transactions):
        self.transactions.pop(index)
    self._refresh_tree()
    self._update_summary()

  def _on_export_csv(self) -> None:
    if not self.transactions:
      messagebox.showinfo("Export", "No transactions to export.")
      return
    filepath = filedialog.asksaveasfilename(
      parent=self.root,
      title="Export Transactions",
      defaultextension=".csv",
      filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
    )
    if not filepath:
      return

    try: 
      lines = ["date,category,memo,amount"]
      for tx in self.transactions:
        memo = tx["memo"].replace('"', '""')
        lines.append(
          f'{tx["date"].isoformat()},{tx["category"]},"{memo}",{tx["amount"]:.2f}'
        )
      Path(filepath).write_text("\n".join(lines), encoding="utf-8")
      messagebox.showinfo("Export", f"Transactions exported to {filepath}.")
    except OSError as exc:
      messagebox.showerror("Export Failed", f"Could not export transactions:\n{exc!s}")

  def _refresh_tree(self) -> None:
    for item in self._tree.get_children():
      self._tree.delete(item)
    for idx, tx in enumerate(self.transactions):
      self._tree.insert(
        "",
        "end",
        text=str(idx),
        values=(
          tx["date"].isoformat(),
          tx["category"],
          tx["memo"],
          f"${tx['amount']:.2f}",
        ),
      )

  def _update_summary(self) -> None:
    income = sum(tx["amount"] for tx in self.transactions if tx["amount"] >= 0)
    expenses = sum(tx["amount"] for tx in self.transactions if tx["amount"] < 0)
    balance = income + expenses
    self._summary_vars["income"].set(f"${income:.2f}")
    self._summary_vars["expenses"].set(f"${expenses:.2f}")
    self._summary_vars["balance"].set(f"${balance:.2f}")

  def _reset_form(self) -> None:
    self._amount_var.set("")
    self._memo_var.set("")
    self._category_var.set("")
    self._date_var.set(date.today().isoformat())