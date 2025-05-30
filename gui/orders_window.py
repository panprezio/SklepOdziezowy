import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.customer import Customer
from models.product import Product
from models.order import Order


class OrderFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        # Pole wyszukiwania
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(search_frame, text="Szukaj klienta:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_orders)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Lista zamówień
        columns = ("ID", "Klient", "Produkt", "Ilość")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)

        # Formularz
        form = ttk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)

        ttk.Label(form, text="Klient").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(form, text="Produkt").grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(form, text="Ilość").grid(row=2, column=0, padx=5, pady=2)

        self.customer_cb = ttk.Combobox(form, values=[c[1] for c in Customer.get_all()])
        self.product_cb = ttk.Combobox(form, values=[p[1] for p in Product.get_all()])
        self.qty_entry = ttk.Entry(form)

        self.customer_cb.grid(row=0, column=1, padx=5, pady=2)
        self.product_cb.grid(row=1, column=1, padx=5, pady=2)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=2)

        # Przyciski
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=5, padx=5)

        ttk.Button(btn_frame, text="Dodaj zamówienie", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_orders).pack(side="left", padx=5)

        self.all_orders = []
        self.load_orders()

    def load_orders(self):
        self.all_orders = Order.get_all()
        self.display_orders(self.all_orders)

    def display_orders(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for o in data:
            self.tree.insert("", "end", values=o)

    def filter_orders(self, *args):
        search = self.search_var.get().lower()
        filtered = [o for o in self.all_orders if search in o[1].lower()]
        self.display_orders(filtered)

    def add_order(self):
        customer = self.customer_cb.get()
        product = self.product_cb.get()
        qty = self.qty_entry.get()
        if not customer or not product or not qty:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return
        try:
            qty_val = int(qty)
            if qty_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Ilość musi być dodatnia")
            return
        Order.add(customer, product, qty_val)
        self.load_orders()
        self.customer_cb.set("")
        self.product_cb.set("")
        self.qty_entry.delete(0, tk.END)

    def get_selected_order(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz zamówienie z listy")
            return None
        item = self.tree.item(sel[0])
        return item["values"]

    def edit_order(self):
        selected = self.get_selected_order()
        if not selected:
            return
        oid, customer, product, qty = selected

        new_customer = simpledialog.askstring("Edytuj klienta", "Klient:", initialvalue=customer)
        new_product = simpledialog.askstring("Edytuj produkt", "Produkt:", initialvalue=product)
        new_qty_str = simpledialog.askstring("Edytuj ilość", "Ilość:", initialvalue=qty)

        if None in (new_customer, new_product, new_qty_str):
            return

        try:
            new_qty = int(new_qty_str)
            if new_qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Ilość musi być liczbą dodatnią")
            return

        Order.update(oid, new_customer, new_product, new_qty)
        self.load_orders()

    def delete_order(self):
        selected = self.get_selected_order()
        if not selected:
            return
        oid = selected[0]
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć to zamówienie?"):
            Order.delete(oid)
            self.load_orders()


