import tkinter as tk
from tkinter import ttk, messagebox
from models.customer import Customer
from models.product import Product
from models.order import Order
from db.db import connect


class OrderFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(search_frame, text="Szukaj zamówienia:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_orders)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.columns = ("ID", "Klient", "Data", "Status", "Produkt", "Rozmiar", "Kolor", "Ilość", "Cena szt.", "Suma")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", selectmode="browse")

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=140, anchor="center", stretch=True)

        tree_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)

        form = ttk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Klient:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.customer_cb = ttk.Combobox(form, values=[f"{c[1]} {c[2]}" for c in Customer.get_all()], font=("Arial", 11))
        self.customer_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.customer_cb.focus()

        ttk.Label(form, text="Produkt:", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.product_cb = ttk.Combobox(form, values=[p[1] for p in Product.get_all()], font=("Arial", 11))
        self.product_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.product_cb.bind("<<ComboboxSelected>>", self.update_variants)

        ttk.Label(form, text="Wariant:", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.variant_cb = ttk.Combobox(form, font=("Arial", 11), state="readonly")
        self.variant_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.variant_cb.bind("<<ComboboxSelected>>", self.update_variant_info)

        ttk.Label(form, text="Ilość:", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.qty_entry = ttk.Entry(form, font=("Arial", 11))
        self.qty_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.qty_entry, "np. 5")

        ttk.Label(form, text="Status:", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.status_cb = ttk.Combobox(form, values=["Oczekujące", "W realizacji", "Wysłane", "Zrealizowane"], font=("Arial", 11))
        self.status_cb.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Rozmiar:", font=("Arial", 11)).grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.size_var = tk.StringVar()
        self.size_entry = ttk.Entry(form, textvariable=self.size_var, font=("Arial", 11), state="readonly")
        self.size_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Kolor:", font=("Arial", 11)).grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.color_var = tk.StringVar()
        self.color_entry = ttk.Entry(form, textvariable=self.color_var, font=("Arial", 11), state="readonly")
        self.color_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        btn_form = ttk.Frame(self)
        btn_form.pack(fill="x", pady=5, padx=5)
        ttk.Button(btn_form, text="Dodaj", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Edytuj", command=self.edit_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Usuń", command=self.delete_order).pack(side="left", padx=5)
        ttk.Button(btn_form, text="Odśwież", command=self.load_orders).pack(side="left", padx=5)

        self.all_orders = []
        self.variant_map = {}
        self.load_orders()

    def add_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(foreground="gray")
        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(entry, placeholder))
        entry.bind("<FocusOut>", lambda e: self.restore_placeholder(entry, placeholder))

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="gray")

    def update_variants(self, event=None):
        product_name = self.product_cb.get()
        if not product_name:
            self.variant_cb['values'] = []
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pv.variant_id, pv.size, pv.color
            FROM product_variants pv
            JOIN products p ON pv.product_id = p.product_id
            WHERE p.name = %s
        """, (product_name,))
        variants = cursor.fetchall()
        conn.close()

        self.variant_map = {f"{size} / {color}": variant_id for variant_id, size, color in variants}
        self.variant_cb['values'] = list(self.variant_map.keys())
        self.variant_cb.set("")
        self.size_var.set("")
        self.color_var.set("")

    def update_variant_info(self, event=None):
        desc = self.variant_cb.get()
        variant_id = self.variant_map.get(desc)
        if not variant_id:
            self.size_var.set("")
            self.color_var.set("")
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT size, color FROM product_variants WHERE variant_id = %s", (variant_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.size_var.set(result[0])
            self.color_var.set(result[1])

    def add_order(self):
        customer_name = self.customer_cb.get()
        product_name = self.product_cb.get()
        variant_desc = self.variant_cb.get()
        qty = self.qty_entry.get()
        status = self.status_cb.get()

        if not all([customer_name, product_name, variant_desc, qty, status]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return

        try:
            qty_val = int(qty)
            if qty_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Ilość musi być dodatnią liczbą")
            return

        variant_id = self.variant_map.get(variant_desc)
        if not variant_id:
            messagebox.showerror("Błąd", "Nieprawidłowy wariant")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT customer_id FROM customers WHERE CONCAT(first_name, ' ', last_name) = %s", (customer_name,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono klienta")
            conn.close()
            return
        customer_id = result[0]

        cursor.execute("""
                       SELECT p.price
                       FROM product_variants pv
                                JOIN products p ON pv.product_id = p.product_id
                       WHERE pv.variant_id = %s
                       """, (variant_id,))
        result = cursor.fetchone()
        if not result:
            raise Exception("Nie znaleziono ceny dla danego wariantu")
        unit_price = result[0]

        if not result:
            messagebox.showerror("Błąd", "Nie znaleziono wariantu")
            conn.close()
            return
        unit_price = result[0]

        total_price = qty_val * float(unit_price)

        cursor.execute("""
            INSERT INTO orders (customer_id, order_date, status, total_price)
            VALUES (%s, NOW(), %s, %s)
        """, (customer_id, status, total_price))
        order_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO order_items (order_id, variant_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, variant_id, qty_val, unit_price))

        conn.commit()
        conn.close()

        self.load_orders()
        self.customer_cb.set("")
        self.product_cb.set("")
        self.variant_cb.set("")
        self.qty_entry.delete(0, tk.END)
        self.status_cb.set("")
        self.size_var.set("")
        self.color_var.set("")
        messagebox.showinfo("Sukces", "Zamówienie dodane")

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

    def sort_by_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverse)
        except Exception:
            data.sort(key=lambda t: t[0], reverse=reverse)

        for index, (_, k) in enumerate(data):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

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
        customer_fullname = selected[1]
        status = selected[3]
        product = selected[4]
        size = selected[5]
        color = selected[6]
        qty = selected[7]
        variant_desc = f"{size} / {color}"

        edit_win = tk.Toplevel(self)
        edit_win.title("Edytuj zamówienie")
        edit_win.grab_set()
        edit_win.resizable(False, False)


        ttk.Label(edit_win, text="Klient:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        customers_data = Customer.get_all()
        customers = [f"{c[1]} {c[2]}" for c in customers_data]
        customer_map = {f"{c[1]} {c[2]}": c[0] for c in customers_data}
        customer_cb = ttk.Combobox(edit_win, values=customers, font=("Arial", 11), state="readonly")
        customer_cb.set(customer_fullname)
        customer_cb.grid(row=0, column=1, padx=10, pady=5)


        ttk.Label(edit_win, text="Produkt:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        products = [p[1] for p in Product.get_all()]
        product_cb = ttk.Combobox(edit_win, values=products, font=("Arial", 11), state="readonly")
        product_cb.set(product)
        product_cb.grid(row=1, column=1, padx=10, pady=5)


        ttk.Label(edit_win, text="Wariant:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        variant_cb = ttk.Combobox(edit_win, font=("Arial", 11), state="readonly")
        variant_cb.grid(row=2, column=1, padx=10, pady=5)


        ttk.Label(edit_win, text="Ilość:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        qty_entry = ttk.Entry(edit_win, width=40)
        qty_entry.insert(0, qty)
        qty_entry.grid(row=3, column=1, padx=10, pady=5)


        ttk.Label(edit_win, text="Status:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        statuses = ["oczekujące", "zrealizowane", "anulowane"]
        status_cb = ttk.Combobox(edit_win, values=statuses, font=("Arial", 11), state="readonly")
        status_cb.set(status)
        status_cb.grid(row=4, column=1, padx=10, pady=5)


        def update_variants_for_product(event=None):
            selected_product = product_cb.get()
            if not selected_product:
                variant_cb['values'] = []
                return

            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT pv.variant_id, pv.size, pv.color
                           FROM product_variants pv
                                    JOIN products p ON pv.product_id = p.product_id
                           WHERE p.name = %s
                           """, (selected_product,))
            variants = cursor.fetchall()
            conn.close()

            self.variant_map = {f"{size} / {color}": variant_id for variant_id, size, color in variants}
            variant_cb['values'] = list(self.variant_map.keys())


            if selected_product == product and variant_desc in self.variant_map:
                variant_cb.set(variant_desc)
            else:
                variant_cb.set("")


        product_cb.bind("<<ComboboxSelected>>", update_variants_for_product)
        update_variants_for_product()


        def save_changes():
            new_customer = customer_cb.get().strip()
            new_product = product_cb.get().strip()
            new_variant = variant_cb.get().strip()
            new_qty_str = qty_entry.get().strip()
            new_status = status_cb.get().strip()

            if not all([new_customer, new_product, new_variant, new_qty_str, new_status]):
                messagebox.showwarning("Błąd", "Wszystkie pola muszą być wypełnione")
                return

            try:
                new_qty = int(new_qty_str)
                if new_qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Błąd", "Ilość musi być liczbą dodatnią")
                return

            variant_id = self.variant_map.get(new_variant)
            if not variant_id:
                messagebox.showerror("Błąd", "Nieprawidłowy wariant (upewnij się, że został wybrany z listy)")
                return

            customer_id = customer_map.get(new_customer)
            if not customer_id:
                messagebox.showerror("Błąd", "Nieprawidłowy klient")
                return

            success = Order.update(order_id=oid, customer_id=customer_id, product_name=new_product,
                                   variant_id=variant_id, quantity=new_qty, status=new_status)
            if success:
                self.load_orders()
                messagebox.showinfo("Sukces", "Zamówienie zaktualizowane")
                edit_win.destroy()
            else:
                messagebox.showerror("Błąd", "Nie udało się edytować zamówienia")

        ttk.Button(edit_win, text="Zapisz zmiany", command=save_changes).grid(
            row=5, column=0, columnspan=2, pady=10
        )

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







