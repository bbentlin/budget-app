import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import date
from pathlib import Path

from budget_app.models.transaction import Transaction
from budget_app.storage.repository import TransactionRepository


class BudgetApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Budget App")
        self.root.geometry("900x560")
        self.root.minsize(780, 480)
        self.root.configure(bg="#f4f5f8")

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
        self._default_categories = [
            "Salary",
            "Bonus",
            "Savings",
            "Rent",
            "Mortgage",
            "Groceries",
            "Dining",
            "Utilities",
            "Insurance",
            "Transportation",
            "Entertainment",
            "Healthcare",
            "Subscriptions",
            "Education",
            "Pets",
            "Miscellaneous",
        ]
        self._tx_kind_var = tk.StringVar(value="Income")
        self._editing_index: int | None = None

        self._configure_style()
        self._build_menu()
        self._build_layout()
        self._style_treeview()
        self._bind_shortcuts()
        self._build_context_menu()
        self._tree.bind("<Double-1>", self._on_start_edit)
        self._tree.bind("<Button-3>", self._open_tree_menu)
        self._tree.bind("<Button-2>", self._open_tree_menu)
        self._tree.bind("<Control-Button-1>", self._open_tree_menu)
        self._refresh_tree()
        self._update_summary()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.root.mainloop()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        palette = {
            "background": "#f4f5f8",
            "surface": "#ffffff",
            "border": "#d0d5dd",
            "accent": "#4c6ef5",
            "accent_hover": "#3b5bdb",
            "danger": "#f03e3e",
            "danger_hover": "#c92a2a",
            "text": "#1f2430",
            "muted": "#667085",
            "stripe_even": "#f9fafc",
            "stripe_odd": "#eef2ff",
        }

        self.root.option_add("*Font", "{Helvetica Neue} 12")
        self.root.option_add("*TCombobox*Font", "{Helvetica Neue} 12")
        self.root.option_add("*TEntry.Font", "{Helvetica Neue} 12")

        style.configure("TFrame", background=palette["background"])
        style.configure("Card.TFrame", background=palette["surface"], borderwidth=0)
        style.configure(
            "CardHeading.TLabel",
            background=palette["surface"],
            foreground=palette["text"],
            font=("Helvetica Neue", 14, "bold"),
        )
        style.configure(
            "Caption.TLabel",
            background=palette["surface"],
            foreground=palette["muted"],
            font=("Helvetica Neue", 11),
        )
        style.configure(
            "Summary.TLabel",
            background=palette["surface"],
            foreground=palette["muted"],
            font=("Helvetica Neue", 13),
        )
        style.configure(
            "SummaryValue.TLabel",
            background=palette["surface"],
            foreground=palette["text"],
            font=("Helvetica Neue", 20, "bold"),
        )
        style.configure(
            "Accent.TButton",
            background=palette["accent"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=3,
            focuscolor=palette["accent_hover"],
            padding=(18, 8),
        )
        style.map(
            "Accent.TButton",
            background=[("active", palette["accent_hover"]), ("pressed", palette["accent_hover"])],
        )
        style.configure(
            "Danger.TButton",
            background=palette["danger"],
            foreground="#ffffff",
            borderwidth=0,
            padding=(18, 8),
        )
        style.map(
            "Danger.TButton",
            background=[("active", palette["danger_hover"]), ("pressed", palette["danger_hover"])],
        )
        style.configure(
            "Treeview",
            background=palette["surface"],
            foreground=palette["text"],
            fieldbackground=palette["surface"],
            borderwidth=0,
            rowheight=30,
        )
        style.map(
            "Treeview",
            background=[("selected", palette["accent"])],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Treeview.Heading",
            background=palette["background"],
            foreground=palette["muted"],
            font=("Helvetica Neue", 12, "bold"),
        )

        self._palette = palette

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Export CSV…", command=self._on_export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        summary_frame = ttk.Frame(container)
        summary_frame.pack(fill="x", pady=(0, 20))
        summary_frame.columnconfigure((0, 1, 2), weight=1)

        for idx, (label, var) in enumerate(self._summary_vars.items()):
            block = ttk.Frame(summary_frame, style="Card.TFrame", padding=18)
            block.grid(row=0, column=idx, sticky="nsew", padx=10)
            ttk.Label(block, text=label.title(), style="Summary.TLabel").pack(anchor="w")
            ttk.Label(block, textvariable=var, style="SummaryValue.TLabel").pack(anchor="w", pady=(6, 0))

        tree_card = ttk.Frame(container, style="Card.TFrame", padding=18)
        tree_card.pack(fill="both", expand=True, pady=(0, 20))
        ttk.Label(tree_card, text="Transactions", style="CardHeading.TLabel").pack(anchor="w", pady=(0, 10))

        tree_container = ttk.Frame(tree_card, style="Card.TFrame")
        tree_container.pack(fill="both", expand=True)

        columns = ("date", "category", "memo", "amount")
        self._tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=10)
        self._tree.heading("date", text="Date")
        self._tree.heading("category", text="Category")
        self._tree.heading("memo", text="Memo")
        self._tree.heading("amount", text="Amount")
        self._tree.column("date", width=110, anchor="center")
        self._tree.column("category", width=160, anchor="w")
        self._tree.column("memo", width=320, anchor="w")
        self._tree.column("amount", width=120, anchor="e")
        self._tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self._tree.yview)
        scrollbar.pack(fill="y", side="right", padx=(8, 0))
        self._tree.configure(yscrollcommand=scrollbar.set)

        tree_actions = ttk.Frame(tree_card, style="Card.TFrame")
        tree_actions.pack(fill="x", pady=(12, 0))
        ttk.Button(tree_actions, text="Edit Selected", command=self._on_start_edit).pack(side="right", padx=(0, 10))
        ttk.Button(tree_actions, text="Delete Selected", style="Danger.TButton", command=self._on_delete_selected).pack(
            side="right"
        )

        form_card = ttk.Frame(container, style="Card.TFrame", padding=18)
        form_card.pack(fill="x")
        ttk.Label(form_card, text="Transaction Details", style="CardHeading.TLabel").grid(
            row=0, column=0, columnspan=7, sticky="w", pady=(0, 12)
        )

        ttk.Label(form_card, text="Date (YYYY-MM-DD)", style="Caption.TLabel").grid(row=1, column=0, sticky="w")
        self._date_entry = ttk.Entry(form_card, textvariable=self._date_var, width=18)
        self._date_entry.grid(row=2, column=0, sticky="we")

        ttk.Label(form_card, text="Category", style="Caption.TLabel").grid(row=1, column=1, sticky="w", padx=(12, 0))
        self._category_combo = ttk.Combobox(
            form_card,
            textvariable=self._category_var,
            values=self._default_categories,
            width=22,
        )
        self._category_combo.grid(row=2, column=1, sticky="we", padx=(12, 0))
        self._category_combo.bind("<Return>", lambda _: self._on_add_transaction())
        self._category_combo.bind("<KP_Enter>", lambda _: self._on_add_transaction())
        self._category_combo.bind("<<ComboboxSelected>>", lambda _: self._category_combo.focus_set())

        ttk.Label(form_card, text="Memo", style="Caption.TLabel").grid(row=1, column=2, sticky="w", padx=(12, 0))
        self._memo_entry = ttk.Entry(form_card, textvariable=self._memo_var)
        self._memo_entry.grid(row=2, column=2, sticky="we", padx=(12, 0))

        ttk.Label(form_card, text="Type", style="Caption.TLabel").grid(row=1, column=3, sticky="w", padx=(12, 0))
        self._type_combo = ttk.Combobox(
            form_card,
            textvariable=self._tx_kind_var,
            values=("Income", "Expense"),
            state="readonly",
            width=14,
        )
        self._type_combo.grid(row=2, column=3, sticky="we", padx=(12, 0))
        self._type_combo.current(0)

        ttk.Label(form_card, text="Amount", style="Caption.TLabel").grid(row=1, column=4, sticky="w", padx=(12, 0))
        self._amount_entry = ttk.Entry(form_card, textvariable=self._amount_var, width=16)
        self._amount_entry.grid(row=2, column=4, sticky="we", padx=(12, 0))

        self._submit_button = ttk.Button(form_card, text="Add", style="Accent.TButton", command=self._on_add_transaction)
        self._submit_button.grid(row=2, column=5, padx=(18, 0))

        self._cancel_button = ttk.Button(form_card, text="Cancel", command=self._on_cancel_edit)
        self._cancel_button.grid(row=2, column=6, padx=(12, 0))
        self._cancel_button.grid_remove()

        for col in range(7):
            form_card.columnconfigure(col, weight=1 if col == 2 else 0)

        self._date_entry.focus_set()

    def _style_treeview(self) -> None:
        self._tree.tag_configure("evenrow", background=self._palette["stripe_even"])
        self._tree.tag_configure("oddrow", background=self._palette["stripe_odd"])

    def _bind_shortcuts(self) -> None:
        def submit(event: tk.Event | None = None) -> str:
            focus_widget = self.root.focus_get()
            form_widgets = {
                self._date_entry,
                self._category_combo,  # <<< swapped in combobox
                self._memo_entry,
                self._type_combo,
                self._amount_entry,
                self._submit_button,
            }
            if focus_widget in form_widgets:
                self._on_add_transaction()
                return "break"
            return ""

        def cancel(event: tk.Event | None = None) -> str:
            if self._editing_index is not None:
                self._on_cancel_edit()
                return "break"
            return ""

        for widget in (
            self._date_entry,
            self._category_combo,  # <<< swapped in combobox
            self._memo_entry,
            self._type_combo,
            self._amount_entry,
            self._submit_button,
        ):
            widget.bind("<Return>", submit)
            widget.bind("<KP_Enter>", submit)

        self.root.bind("<Escape>", cancel)
        self.root.bind("<Return>", submit)
        self.root.bind("<KP_Enter>", submit)

    def _build_context_menu(self) -> None:
        self._tree_menu = tk.Menu(self.root, tearoff=False)
        self._tree_menu.add_command(label="Edit", command=self._on_start_edit)
        self._tree_menu.add_command(label="Delete", command=self._on_delete_selected)
        self._tree_menu.add_separator()
        self._tree_menu.add_command(label="Export CSV…", command=self._on_export_csv)

    def _open_tree_menu(self, event: tk.Event) -> None:
        item_id = self._tree.identify_row(event.y)
        if item_id:
            self._tree.selection_set(item_id)
            self._tree.focus(item_id)
        try:
            self._tree_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._tree_menu.grab_release()

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
            focus_index = len(self.transactions) - 1
            if not self._persist():
                self.transactions.pop()
                return
        else:
            index = self._editing_index
            previous = self.transactions[index]
            self.transactions[index] = transaction
            focus_index = index
            if not self._persist():
                self.transactions[index] = previous
                return

        self._refresh_tree(focus_index=focus_index)
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

    def _refresh_tree(self, *, focus_index: int | None = None) -> None:
        self._tree.delete(*self._tree.get_children())
        item_ids: list[str] = []
        for idx, tx in enumerate(self.transactions):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            item_id = self._tree.insert(
                "",
                "end",
                text=str(idx),
                values=(
                    tx.date.isoformat(),
                    tx.category,
                    tx.memo,
                    f"${tx.amount:.2f}",
                ),
                tags=(tag,),
            )
            item_ids.append(item_id)

        if focus_index is not None and 0 <= focus_index < len(item_ids):
            item_id = item_ids[focus_index]
            self._tree.selection_set(item_id)
            self._tree.focus(item_id)
            self._tree.see(item_id)
        elif item_ids:
            self._tree.see(item_ids[-1])

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
        self._category_combo.set("")  # <<< clear combo selection
        self._date_var.set(date.today().isoformat())
        self._tx_kind_var.set("Income")
        self._type_combo.current(0)
        self._date_entry.focus_set()

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
        self._category_combo.set(tx.category)  # <<< populate combo during edit
        self._memo_var.set(tx.memo)
        self._amount_var.set(format(abs(tx.amount), "f"))
        self._tx_kind_var.set("Income" if tx.amount >= 0 else "Expense")
        self._type_combo.set("Income" if tx.amount >= 0 else "Expense")
        self._submit_button.config(text="Save")
        self._cancel_button.grid()
        self._date_entry.focus_set()

    def _on_cancel_edit(self) -> None:
        self._exit_edit_mode()
        self._reset_form()

    def _exit_edit_mode(self) -> None:
        self._editing_index = None
        self._submit_button.config(text="Add")
        self._cancel_button.grid_remove()