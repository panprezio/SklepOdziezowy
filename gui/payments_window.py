import tkinter as tk
from tkinter import ttk, messagebox
from db.db import connect
from datetime import datetime

class PaymentsFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)


        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=10, padx=10)

        ttk.Label(search_frame, text="Szukaj płatności:", font=("Arial", 10)).pack(side="left", padx=(5, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_payments)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=(0, 5))


        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10)

        columns = ("ID", "Zamówienie", "Data", "Kwota", "Metoda", "Status")
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

        ttk.Label(form, text="Zamówienie:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.order_cb = ttk.Combobox(form, font=("Arial", 11), state="readonly")
        self.order_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Kwota:", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount = ttk.Entry(form, font=("Arial", 11))
        self.amount.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Metoda:", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.method = ttk.Combobox(form, font=("Arial", 11), state="readonly", values=["Przelew", "Karta", "BLIK", "Gotówka"])
        self.method.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Status:", font=("Arial", 11)).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.status = ttk.Combobox(form, font=("Arial", 11), state="readonly", values=["zrealizowana", "oczekująca", "odrzucona"])
        self.status.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        form.columnconfigure(1, weight=1)


        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10, padx=10)

        ttk.Button(btn_frame, text="Dodaj", command=self.add_payment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete_payment).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_payments).pack(side="left", padx=5)

        self.all_payments = []
        self.orders_map = {}
        self.load_orders()
        self.load_payments()

    def sort_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def load_orders(self):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT order_id FROM orders")
            orders = cursor.fetchall()
            conn.close()

            self.orders_map = {str(order_id): order_id for (order_id,) in orders}
            self.order_cb["values"] = list(self.orders_map.keys())
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować zamówień: {e}")

    def load_payments(self):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payment_id, order_id, payment_date, amount, payment_method, status
                FROM payments
            """)
            self.all_payments = cursor.fetchall()
            conn.close()
            self.display_payments(self.all_payments)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować płatności: {e}")

    def display_payments(self, data):
        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))

        self.tree.tag_configure('evenrow', background="#f4f4f4")
        self.tree.tag_configure('oddrow', background="#ffffff")

    def filter_payments(self, *args):
        search = self.search_var.get().lower()
        filtered = [row for row in self.all_payments if search in " ".join(str(i).lower() for i in row)]
        self.display_payments(filtered)

    def add_payment(self):
        order_id = self.order_cb.get()
        amount = self.amount.get()
        method = self.method.get()
        status = self.status.get()

        if not all([order_id, amount, method, status]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return

        try:
            amount_val = float(amount)
            if amount_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Błąd", "Kwota musi być dodatnią liczbą")
            return

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO payments (order_id, payment_date, amount, payment_method, status)
                VALUES (%s, NOW(), %s, %s, %s)
            """, (self.orders_map[order_id], amount_val, method, status))
            conn.commit()
            conn.close()
            self.load_payments()
            self.clear_form()
            messagebox.showinfo("Sukces", "Płatność dodana")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def delete_payment(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz płatność z listy")
            return
        pid = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tę płatność?"):
            try:
                conn = connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM payments WHERE payment_id=%s", (pid,))
                conn.commit()
                conn.close()
                self.load_payments()
                messagebox.showinfo("Sukces", "Płatność usunięta")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def clear_form(self):
        self.order_cb.set("")
        self.amount.delete(0, tk.END)
        self.method.set("")
        self.status.set("")
