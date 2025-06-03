import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.customer import Customer
from models.product import Product
from models.order import Order

class OrderFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)


        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(search_frame, text="Szukaj klienta:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_orders)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)


        self.columns = ("ID", "Klient", "Data", "Status", "Produkt", "Rozmiar", "Kolor", "Ilość", "Cena szt.", "Suma")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", selectmode="browse")

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=100, anchor="center", stretch=True)


        tree_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)


        form = ttk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)

        ttk.Label(form, text="Klient:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.customer_cb = ttk.Combobox(form, values=[f"{c[1]} {c[2]}" for c in Customer.get_all()])
        self.customer_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.customer_cb.focus()

        ttk.Label(form, text="Produkt:", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.product_cb = ttk.Combobox(form, values=[p[1] for p in Product.get_all()])
        self.product_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Ilość:", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.qty_entry = ttk.Entry(form)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.qty_entry, "np. 5")

        ttk.Label(form, text="Status:", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.status_cb = ttk.Combobox(form, values=["Oczekujące", "W realizacji", "Wysłane", "Zrealizowane"])
        self.status_cb.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Rozmiar:", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.size_entry = ttk.Entry(form)
        self.size_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.size_entry, "np. M")

        ttk.Label(form, text="Kolor:", font=("Arial", 11)).grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.color_entry = ttk.Entry(form)
        self.color_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.color_entry, "np. Czarny")


        btn_form = ttk.Frame(self)
        btn_form.pack(fill="x", pady=5, padx=5)
        ttk.Button(btn_form, text="Dodaj zamówienie", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Edytuj zamówienie", command=self.edit_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Usuń zamówienie", command=self.delete_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Odśwież", command=self.load_orders).pack(side="left", padx=5)

        self.all_orders = []
        self.load_orders()

    def add_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(entry, placeholder))
        entry.bind("<FocusOut>", lambda e: self.restore_placeholder(entry, placeholder))

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)

    def sort_by_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverse)
        except Exception:
            data.sort(key=lambda t: t[0], reverse=reverse)

        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def load_orders(self):
        self.all_orders = Order.get_all()
        self.display_orders(self.all_orders)

    def display_orders(self, data):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))
        self.tree.tag_configure("even", background="#f8f8ff")
        self.tree.tag_configure("odd", background="#ffffff")

    def filter_orders(self, *args):
        search = self.search_var.get().lower()
        filtered = [row for row in self.all_orders if search in " ".join(str(i).lower() for i in row)]
        self.display_orders(filtered)

    def add_order(self):
        customer_name = self.customer_cb.get()
        product_name = self.product_cb.get()
        qty = self.qty_entry.get()
        status = self.status_cb.get()
        size = self.size_entry.get()
        color = self.color_entry.get()

        if not all([customer_name, product_name, qty, status, size, color]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return

        try:
            qty_val = int(qty)
            if qty_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Ilość musi być dodatnią liczbą")
            return

        success = Order.add(customer_name, product_name, qty_val, status, size, color)
        if success:
            self.load_orders()
            self.customer_cb.set("")
            self.product_cb.set("")
            self.qty_entry.delete(0, tk.END)
            self.status_cb.set("")
            self.size_entry.delete(0, tk.END)
            self.color_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Błąd", "Nie udało się dodać zamówienia")

    def get_selected_order(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz zamówienie z listy")
            return None
        return self.tree.item(sel[0])["values"]

    def edit_order(self):
        selected = self.get_selected_order()
        if not selected:
            return

        oid = selected[0]
        customer = selected[1]
        status = selected[3]
        product = selected[4]
        size = selected[5]
        color = selected[6]
        qty = selected[7]

        new_customer = simpledialog.askstring("Edytuj klienta", "Klient:", initialvalue=customer)
        new_status = simpledialog.askstring("Edytuj status", "Status:", initialvalue=status)
        new_product = simpledialog.askstring("Edytuj produkt", "Produkt:", initialvalue=product)
        new_size = simpledialog.askstring("Edytuj rozmiar", "Rozmiar:", initialvalue=size)
        new_color = simpledialog.askstring("Edytuj kolor", "Kolor:", initialvalue=color)
        new_qty_str = simpledialog.askstring("Edytuj ilość", "Ilość:", initialvalue=qty)

        if None in (new_customer, new_status, new_product, new_size, new_color, new_qty_str):
            return

        try:
            new_qty = int(new_qty_str)
            if new_qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Ilość musi być liczbą dodatnią")
            return

        success = Order.update(oid, new_customer, new_product, new_qty, new_status, new_size, new_color)
        if success:
            self.load_orders()
        else:
            messagebox.showerror("Błąd", "Nie udało się edytować zamówienia")

    def delete_order(self):
        selected = self.get_selected_order()
        if not selected:
            return
        oid = selected[0]
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć to zamówienie?"):
            success = Order.delete(oid)
            if success:
                self.load_orders()
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć zamówienia")






