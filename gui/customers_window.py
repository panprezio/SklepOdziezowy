import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models.customer import Customer
import re
from db.db import connect


class CustomerFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)


        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('TkDefaultFont', 10))
        style.map("Treeview", background=[("selected", "#ececec")])
        style.configure("Treeview.Heading", font=('TkDefaultFont', 10, 'bold'))

        self.tree_tag_even = "evenrow"
        self.tree_tag_odd = "oddrow"
        self.tree = None
        self.setup_styles()


        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)


        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        form = ttk.LabelFrame(left_frame, text="Dane klienta")
        form.pack(fill="x", pady=5)

        labels = ["Imię", "Nazwisko", "Email"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(form, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label.lower()] = entry

        btn_frame = ttk.LabelFrame(left_frame, text="Akcje")
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Dodaj klienta", command=self.add_customer).pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Edytuj klienta", command=self.edit_customer).pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Usuń klienta", command=self.delete_customer).pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_customers).pack(fill="x", padx=5, pady=2)


        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(search_frame, text="Szukaj:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_customers)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)

        columns = ("ID", "Imię", "Nazwisko", "Email")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.all_customers = []
        self.load_customers()

    def setup_styles(self):
        style = ttk.Style()
        style.configure(self.tree_tag_even, background="#f2f2f2")
        style.configure(self.tree_tag_odd, background="#ffffff")

    def load_customers(self):
        try:
            self.all_customers = Customer.get_all()
            self.display_customers(self.all_customers)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać klientów: {e}")

    def display_customers(self, data):
        self.tree.delete(*self.tree.get_children())
        for idx, c in enumerate(data):
            tag = self.tree_tag_even if idx % 2 == 0 else self.tree_tag_odd
            self.tree.insert("", "end", values=c, tags=(tag,))

    def filter_customers(self, *args):
        search = self.search_var.get().lower()
        filtered = [
            c for c in self.all_customers
            if any(search in str(field).lower() for field in c[1:])
        ]
        self.display_customers(filtered)

    def valid_email(self, email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

    def get_selected_customer(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz klienta z listy")
            return None
        return self.tree.item(sel[0])["values"]

    def add_customer(self):
        fname = self.entries["imię"].get().strip()
        lname = self.entries["nazwisko"].get().strip()
        email = self.entries["email"].get().strip()

        if not fname or not lname or not email:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return
        if not self.valid_email(email):
            messagebox.showwarning("Błąd", "Podaj poprawny adres email")
            return

        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers WHERE email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Błąd", "Klient z takim adresem email już istnieje.")
                conn.close()
                return

            cursor.execute(
                "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s)",
                (fname, lname, email)
            )
            conn.commit()
            conn.close()
            self.load_customers()
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            messagebox.showinfo("Sukces", "Klient został dodany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się dodać klienta: {e}")

    def edit_customer(self):
        selected = self.get_selected_customer()
        if not selected:
            return

        cid, fname, lname, email = selected

        new_fname = simpledialog.askstring("Edytuj klienta", "Imię:", initialvalue=fname)
        if new_fname is None: return

        new_lname = simpledialog.askstring("Edytuj klienta", "Nazwisko:", initialvalue=lname)
        if new_lname is None: return

        new_email = simpledialog.askstring("Edytuj klienta", "Email:", initialvalue=email)
        if new_email is None or not self.valid_email(new_email):
            messagebox.showwarning("Błąd", "Podaj poprawny adres email")
            return

        try:
            conn = connect()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id = %s", (cid,))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Błąd", "Klient nie istnieje.")
                conn.close()
                return

            cursor.execute("SELECT COUNT(*) FROM customers WHERE email = %s AND customer_id != %s", (new_email, cid))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Błąd", "Adres email jest już przypisany innemu klientowi.")
                conn.close()
                return

            cursor.execute(
                "UPDATE customers SET first_name=%s, last_name=%s, email=%s WHERE customer_id=%s",
                (new_fname, new_lname, new_email, cid)
            )
            conn.commit()
            conn.close()
            self.load_customers()
            messagebox.showinfo("Sukces", "Dane klienta zostały zaktualizowane")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def delete_customer(self):
        selected = self.get_selected_customer()
        if not selected:
            return
        cid = selected[0]
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć wybranego klienta?"):
            try:
                conn = connect()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM customers WHERE customer_id=%s", (cid,))
                conn.commit()
                conn.close()
                self.load_customers()
                messagebox.showinfo("Sukces", "Klient został usunięty")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")






