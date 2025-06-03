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

        ttk.Label(search_frame, text="Szukaj produktu:", font=("Arial", 10)).pack(side="left", padx=(5, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_products)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))


        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10)

        columns = ("ID", "Nazwa", "Opis", "Cena", "Kategoria", "Marka", "Data dodania")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=140, anchor="center", stretch=True)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))


        form = ttk.Frame(self)
        form.pack(fill="x", padx=10, pady=10)


        ttk.Label(form, text="Nazwa:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name = ttk.Entry(form, font=("Arial", 11))
        self.name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.name, "np. Koszulka")


        ttk.Label(form, text="Opis:", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.description = ttk.Entry(form, font=("Arial", 11))
        self.description.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.description, "np. Bawełniana koszulka z nadrukiem")


        ttk.Label(form, text="Cena:", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price = ttk.Entry(form, font=("Arial", 11))
        self.price.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.price, "np. 49.99")


        ttk.Label(form, text="Kategoria:", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.category_cb = ttk.Combobox(form, state="readonly", font=("Arial", 11))
        self.category_cb.grid(row=3, column=1, padx=5, pady=5, sticky="ew")


        ttk.Label(form, text="Marka:", font=("Arial", 11)).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.brand_cb = ttk.Combobox(form, state="readonly", font=("Arial", 11))
        self.brand_cb.grid(row=4, column=1, padx=5, pady=5, sticky="ew")


        form.columnconfigure(1, weight=1)


        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10, padx=10)

        ttk.Button(btn_frame, text="Dodaj", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_products).pack(side="left", padx=5)

        self.all_products = []
        self.load_categories_and_brands()
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

        self.tree.tag_configure('evenrow', background="#eaf4fc")
        self.tree.tag_configure('oddrow', background="#ffffff")

    def add_placeholder(self, entry_widget, placeholder_text):
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(foreground="grey")

        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, "end")
                entry_widget.config(foreground="black")

        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.config(foreground="grey")

        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

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

        edit_win = tk.Toplevel(self)
        edit_win.title("Edytuj produkt")
        edit_win.grab_set()
        edit_win.resizable(False, False)

        ttk.Label(edit_win, text="Nazwa:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = ttk.Entry(edit_win, width=40)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Opis:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        desc_entry = ttk.Entry(edit_win, width=40)
        desc_entry.insert(0, desc)
        desc_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Cena:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        price_entry = ttk.Entry(edit_win, width=40)
        price_entry.insert(0, price)
        price_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Kategoria:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        cat_entry = ttk.Entry(edit_win, width=40)
        cat_entry.insert(0, cat_name)
        cat_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Marka:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        brand_entry = ttk.Entry(edit_win, width=40)
        brand_entry.insert(0, brand_name)
        brand_entry.grid(row=4, column=1, padx=10, pady=5)

        def save_changes():
            new_name = name_entry.get().strip()
            new_desc = desc_entry.get().strip()
            new_price_str = price_entry.get().strip()
            new_cat = cat_entry.get().strip()
            new_brand = brand_entry.get().strip()

            if not all([new_name, new_desc, new_price_str, new_cat, new_brand]):
                messagebox.showwarning("Błąd", "Wszystkie pola muszą być wypełnione")
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
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

        ttk.Button(edit_win, text="Zapisz zmiany", command=save_changes).grid(
            row=5, column=0, columnspan=2, pady=10
        )

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






