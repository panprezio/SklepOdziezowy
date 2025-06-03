import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.product import Product
import re
from db.db import connect

class ProductFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)


        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=10, padx=10)
        ttk.Label(search_frame, text="Szukaj:", font=("Arial", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)


        columns = ("ID", "Nazwa", "Opis", "Cena", "Kategoria", "Marka", "Data dodania")
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, pady=5, padx=5)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=140)


        form = ttk.Frame(self)
        form.pack(fill="x", pady=10, padx=10)

        ttk.Label(form, text="Nazwa").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Opis").grid(row=1, column=0, sticky="w")
        ttk.Label(form, text="Cena").grid(row=2, column=0, sticky="w")
        ttk.Label(form, text="Kategoria").grid(row=3, column=0, sticky="w")
        ttk.Label(form, text="Marka").grid(row=4, column=0, sticky="w")

        self.name = ttk.Entry(form)
        self.name.insert(0, "np. Koszulka")
        self.description = ttk.Entry(form)
        self.description.insert(0, "np. Bawełniana koszulka z nadrukiem")
        self.price = ttk.Entry(form)
        self.price.insert(0, "np. 49.99")
        self.category_cb = ttk.Combobox(form, state="readonly")
        self.brand_cb = ttk.Combobox(form, state="readonly")

        self.name.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.description.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.price.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.category_cb.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.brand_cb.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        form.columnconfigure(1, weight=1)

        self.load_categories_and_brands()


        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10, padx=10)

        ttk.Button(btn_frame, text="Dodaj produkt", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj produkt", command=self.edit_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń produkt", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_products).pack(side="left", padx=5)

        self.all_products = []
        self.load_products()

    def sort_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def load_categories_and_brands(self):
        self.categories = {}
        self.brands = {}
        try:
            conn = connect()
            cursor = conn.cursor()

            cursor.execute("SELECT category_id, name FROM categories")
            for cid, cname in cursor.fetchall():
                self.categories[cname] = cid

            cursor.execute("SELECT brand_id, name FROM brands")
            for bid, bname in cursor.fetchall():
                self.brands[bname] = bid

            conn.close()

            self.category_cb["values"] = list(self.categories.keys())
            self.brand_cb["values"] = list(self.brands.keys())

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować kategorii/marek: {e}")

    def load_products(self):
        try:
            conn = connect()
            cursor = conn.cursor()

            query = """
                SELECT p.product_id, p.name, p.description, p.price,
                       c.name AS category, b.name AS brand, p.created_at
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN brands b ON p.brand_id = b.brand_id
            """

            cursor.execute(query)
            self.all_products = cursor.fetchall()
            conn.close()
            self.display_products(self.all_products)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować produktów: {e}")

    def display_products(self, data):
        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))
        self.tree.tag_configure('evenrow', background="#f9f9f9")
        self.tree.tag_configure('oddrow', background="#ffffff")

    def filter_products(self, *args):
        search = self.search_var.get().lower()
        filtered = [row for row in self.all_products if search in " ".join(str(item).lower() for item in row)]
        self.display_products(filtered)

    def get_selected_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz produkt z listy")
            return None
        return self.tree.item(sel[0])["values"]

    def add_product(self):
        name = self.name.get().strip()
        description = self.description.get().strip()
        price = self.price.get().strip()
        category = self.category_cb.get()
        brand = self.brand_cb.get()

        if not all([name, description, price, category, brand]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return

        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Cena musi być dodatnią liczbą")
            return

        category_id = self.categories.get(category)
        brand_id = self.brands.get(brand)

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, description, price, category_id, brand_id, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (name, description, price_val, category_id, brand_id))
            conn.commit()
            conn.close()
            self.load_products()
            self.clear_form()
            messagebox.showinfo("Sukces", "Produkt dodany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def edit_product(self):
        selected = self.get_selected_product()
        if not selected:
            return
        pid, name, desc, price, cat_name, brand_name, *_ = selected

        new_name = simpledialog.askstring("Edytuj nazwę", "Nazwa:", initialvalue=name)
        new_desc = simpledialog.askstring("Edytuj opis", "Opis:", initialvalue=desc)
        new_price_str = simpledialog.askstring("Edytuj cenę", "Cena:", initialvalue=price)
        new_cat = simpledialog.askstring("Edytuj kategorię", "Kategoria:", initialvalue=cat_name)
        new_brand = simpledialog.askstring("Edytuj markę", "Marka:", initialvalue=brand_name)

        if None in (new_name, new_desc, new_price_str, new_cat, new_brand):
            return

        try:
            new_price = float(new_price_str)
            if new_price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Cena musi być dodatnią liczbą")
            return

        category_id = self.categories.get(new_cat)
        brand_id = self.brands.get(new_brand)

        if category_id is None or brand_id is None:
            messagebox.showwarning("Błąd", "Nieprawidłowa kategoria lub marka")
            return

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products
                SET name=%s,
                    description=%s,
                    price=%s,
                    category_id=%s,
                    brand_id=%s
                WHERE product_id = %s
            """, (new_name, new_desc, new_price, category_id, brand_id, pid))
            conn.commit()
            conn.close()
            self.load_products()
            messagebox.showinfo("Sukces", "Produkt zaktualizowany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def clear_form(self):
        self.name.delete(0, tk.END)
        self.description.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.category_cb.set("")
        self.brand_cb.set("")

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






