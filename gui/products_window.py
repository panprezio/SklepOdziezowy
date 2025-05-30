import tkinter as tk
from tkinter import ttk, messagebox
from models.product import Product
import re
from tkinter import simpledialog, messagebox
from db.db import connect

class ProductFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        # Pole wyszukiwania
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(search_frame, text="Szukaj:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        columns = ("ID", "Nazwa", "Cena")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)

        form = ttk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)

        ttk.Label(form, text="Nazwa").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(form, text="Cena").grid(row=1, column=0, padx=2, pady=2)

        self.name = ttk.Entry(form)
        self.price = ttk.Entry(form)
        self.name.grid(row=0, column=1, padx=2, pady=2)
        self.price.grid(row=1, column=1, padx=2, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=5, padx=5)

        ttk.Button(btn_frame, text="Dodaj produkt", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj produkt", command=self.edit_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń produkt", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_products).pack(side="left", padx=5)

        self.all_products = []
        self.load_products()

    def load_products(self):
        self.all_products = Product.get_all()
        self.display_products(self.all_products)

    def display_products(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in data:
            self.tree.insert("", "end", values=(p[0], p[1], f"{p[2]:.2f}"))

    def filter_products(self, *args):
        search = self.search_var.get().lower()
        filtered = [p for p in self.all_products if search in p[1].lower()]
        self.display_products(filtered)

    def add_product(self):
        name = self.name.get().strip()
        price = self.price.get().strip()
        if not name or not price:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return
        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Cena musi być dodatnią liczbą")
            return
        Product.add(name, price_val)
        self.load_products()
        self.name.delete(0, tk.END)
        self.price.delete(0, tk.END)

    def get_selected_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz produkt z listy")
            return None
        item = self.tree.item(sel[0])
        return item["values"]

    def edit_product(self):
        selected = self.get_selected_product()
        if not selected:
            return
        pid, name, price = selected

        new_name = simpledialog.askstring("Edytuj produkt", "Nazwa:", initialvalue=name)
        if new_name is None:
            return

        new_price_str = simpledialog.askstring("Edytuj produkt", "Cena:", initialvalue=price)
        if new_price_str is None:
            return

        try:
            new_price = float(new_price_str)
            if new_price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Cena musi być dodatnią liczbą")
            return

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET name=%s, price=%s WHERE product_id=%s",
                           (new_name, new_price, pid))
            conn.commit()
            conn.close()
            self.load_products()
            messagebox.showinfo("Sukces", "Produkt został zaktualizowany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def delete_product(self):
        selected = self.get_selected_product()
        if not selected:
            return
        pid = selected[0]
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć ten produkt?"):
            try:
                conn = connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE product_id=%s", (pid,))
                conn.commit()
                conn.close()
                self.load_products()
                messagebox.showinfo("Sukces", "Produkt został usunięty")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")




