import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import date
from pathlib import Path

from budget_app.storage.repository import TransactionRepository
from budget_app.models.transaction import Transaction

class BudgetApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Budget App")
        self.root.geometry("800x520")
        self.root.minsize(720, 440)
        self.root.configure(bg="#f5f5f7")

        data_path = Path.home() / ".budget_app" / "transactions.json"
        self._repository = TransactionRepository(data_path)
        self.transactions: list[Transaction] = self._repository.load()

        self._summary_vars: dict[str, tk.StringVar] = {
            "balance": tk.StringVar(value="$0.00"),
            "income": tk.StringVar(value="$0.00"),
            "expenses": tk.StringVar(value="$0.00"),
        }

        self._amount_var = tk.StringVar()
        self._category_var = tk.StringVar()
        self._memo_var = tk.StringVar()
        self._date_var = tk.StringVar(value=date.today().isoformat())
        self._tx_kind_var = tk.StringVar(value="Income")
        self._editing_index: int | None = None

        self._configure_style()
        self._build_menu()
        self._build_layout()
        self._tree.bind("<Double-1>", self._on_start_edit)
        self._refresh_tree()
        self._update_summary()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.root.mainloop()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        primary_bg = "#f5f5f7"
        surface_bg = "#ffffff"
        accent = "#2d7ff9"
        accent_darker = "#1f5ebe"
        text_primary = "#1c1c1e"
        text_muted = "#6e6e73"

        style.configure("TFrame", background=primary_bg)
        style.configure("TLabelframe", background=primary_bg, borderwidth=0)
        style.configure("TLabelframe.Label", background=primary_bg, foreground=text_muted)
        style.configure("Summary.TFrame", background=surface_bg, relief="flat")
        style.configure("Summary.TLabel", background=surface_bg, foreground=text_muted, font=("Helvetica Neue", 13))
        style.configure("SummaryValue.TLabel", background=surface_bg, foreground=text_primary, font=("Helvetica Neue", 18, "bold"))

        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=3,
            focuscolor=accent_darker,
            padding=(16, 8),
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_darker), ("pressed", accent_darker)],
        )

        style.configure(
            "Treeview",
            background=surface_bg,
            foreground=text_primary,
            fieldbackground=surface_bg,
            bordercolor=primary_bg,
            rowheight=28,
        )
        style.map("Treeview", background=[("selected", accent), ("!selected", surface_bg)], foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading", background=primary_bg, foreground=text_muted, font=("Helvetica Neue", 12, "bold"))

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
        ttk.Button(tree_actions, text="Delete Selected", command=self._on_delete_selected).pack(side="right")
        ttk.Button(tree_actions, text="Edit Selected", command=self._on_start_edit).pack(side="right", padx=(0, 8))

        form = ttk.LabelFrame(container, text="Add Transaction", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self._date_var, width=18).grid(row=1, column=0, sticky="w")

        ttk.Label(form, text="Category").grid(row=0, column=1, sticky="w", padx=(12, 0))
        ttk.Entry(form, textvariable=self._category_var, width=18).grid(row=1, column=1, sticky="w", padx=(12, 0))

        ttk.Label(form, text="Memo").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Entry(form, textvariable=self._memo_var, width=30).grid(row=1, column=2, sticky="w", padx=(12, 0))

        ttk.Label(form, text="Type").grid(row=0, column=3, sticky="w", padx=(12, 0))
        ttk.Combobox(
            form,
            textvariable=self._tx_kind_var,
            values=("Income", "Expense"),
            state="readonly",
            width=12,
        ).grid(row=1, column=3, sticky="w", padx=(12, 0))

        ttk.Label(form, text="Amount").grid(row=0, column=4, sticky="w", padx=(12, 0))
        ttk.Entry(form, textvariable=self._amount_var, width=14).grid(row=1, column=4, sticky="w", padx=(12, 0))

        self._submit_button = ttk.Button(form, text="Add", command=self._on_add_transaction)
        self._submit_button.grid(row=1, column=5, padx=(18, 0))

        self._cancel_button = ttk.Button(form, text="Cancel", command=self._on_cancel_edit)
        self._cancel_button.grid(row=1, column=6, padx=(12, 0))
        self._cancel_button.grid_remove()

        for col in range(7):
            form.columnconfigure(col, weight=1 if col == 2 else 0)

    def _on_add_transaction(self) -> None:
        try:
            transaction = Transaction.from_input(
                raw_amount=self._amount_var.get(),
                raw_category=self._category_var.get(),
                raw_memo=self._memo_var.get(),
                raw_date=self._date_var.get(),
                raw_kind=self._tx_kind_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Invalid Input", str(exc))
            return

        if self._editing_index is None:
            self.transactions.append(transaction)
            if not self._persist():
                self.transactions.pop()
                return
        else:
            index = self._editing_index
            previous = self.transactions[index]
            self.transactions[index] = transaction
            if not self._persist():
                self.transactions[index] = previous
                return

        self._refresh_tree()
        self._update_summary()
        self._exit_edit_mode()
        self._reset_form()

    def _on_delete_selected(self) -> None:
        selected = self._tree.selection()
        if not selected:
            messagebox.showinfo("Delete Transaction", "Select at least one transaction to delete.")
            return 
        
        indexes = sorted(
            (int(self._tree.item(item_id, "text")) for item_id in selected),
            reverse=True,
        )
        removed: list[tuple[int, Transaction]] = []
        for index in indexes:
            if 0 <= index < len(self.transactions):
                removed.append((index, self.transactions.pop(index)))
        
        if not removed:
            return

        self._exit_edit_mode()
        if not self._persist():
            for index, tx in reversed(removed):
                self.transactions.insert(index, tx)
            return
        
        self._refresh_tree()
        self._update_summary()
        self._reset_form()

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
                memo = tx.memo.replace('"', '""')
                lines.append(
                    f'{tx.date.isoformat()},{tx.category},"{memo}",{tx.amount:.2f}'
                )
            Path(filepath).write_text("\n".join(lines), encoding="utf-8")
            messagebox.showinfo("Export", f"Transactions exported to {filepath}.")
        except OSError as exc:
            messagebox.showerror("Export Failed", f"Could not export transactions:\n{exc!s}")

    def _style_treeview(self) -> None:
        self._tree.tag_configure("oddrow", background="#f0f6ff")
        self._tree.tag_configure("evenrow", background="#ffffff")

    def _refresh_tree(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        for idx, tx in enumerate(self.transactions):
            self._tree.insert(
                "",
                "end",
                text=str(idx),
                values=(
                    tx.date.isoformat(),
                    tx.category,
                    tx.memo,
                    f"${tx.amount:.2f}",
                ),
                tags=("evenrow" if idx % 2 == 0 else "oddrow",),
            )

    def _update_summary(self) -> None:
        income = sum(tx.amount for tx in self.transactions if tx.amount >= 0)
        expenses = sum(tx.amount for tx in self.transactions if tx.amount < 0)
        balance = income + expenses
        self._summary_vars["income"].set(f"${income:.2f}")
        self._summary_vars["expenses"].set(f"${expenses:.2f}")
        self._summary_vars["balance"].set(f"${balance:.2f}")

    def _reset_form(self) -> None:
        self._amount_var.set("")
        self._memo_var.set("")
        self._category_var.set("")
        self._date_var.set(date.today().isoformat())
        self._tx_kind_var.set("Income")

    def _persist(self) -> bool:
        try:
            self._repository.save(self.transactions)
        except OSError as exc:
            messagebox.showerror("Save Failed", f"Could not save transactions:\n{exc!s}")
            return False
        return True

    def _on_close(self) -> None:
        if self._persist():
            self.root.destroy()

    def _on_start_edit(self, event: tk.Event | None = None) -> None:
        if event is not None:
            item_id = self._tree.identify_row(event.y)
            if item_id:
                self._tree.selection_set(item_id)

        selected = self._tree.selection()
        if not selected:
            if event is None:
                messagebox.showinfo("Edit Transaction", "Select a transaction to edit.")
            return

        index = int(self._tree.item(selected[0], "text"))
        if not (0 <= index < len(self.transactions)):
            return

        tx = self.transactions[index]
        self._editing_index = index
        self._date_var.set(tx.date.isoformat())
        self._category_var.set(tx.category)
        self._memo_var.set(tx.memo)
        self._amount_var.set(format(abs(tx.amount), "f"))
        self._tx_kind_var.set("Income" if tx.amount >= 0 else "Expense")
        self._submit_button.config(text="Save")
        self._cancel_button.grid()

    def _on_cancel_edit(self) -> None:
        self._exit_edit_mode()
        self._reset_form()

    def _exit_edit_mode(self) -> None:
        self._editing_index = None
        self._submit_button.config(text="Add")
        self._cancel_button.grid_remove()