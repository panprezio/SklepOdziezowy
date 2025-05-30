import tkinter as tk
from tkinter import ttk, messagebox
from models.customer import Customer
import re
from tkinter import simpledialog, messagebox
from db.db import connect

class CustomerFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        # --- Dodaj pole wyszukiwania ---
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(search_frame, text="Szukaj:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_customers)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        # --- Tabela ---
        columns = ("ID", "Imię", "Nazwisko", "Email")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)

        # --- Formularz dodawania nowego klienta ---
        form = ttk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)

        ttk.Label(form, text="Imię").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(form, text="Nazwisko").grid(row=1, column=0, padx=2, pady=2)
        ttk.Label(form, text="Email").grid(row=2, column=0, padx=2, pady=2)

        self.fname = ttk.Entry(form)
        self.lname = ttk.Entry(form)
        self.email = ttk.Entry(form)
        self.fname.grid(row=0, column=1, padx=2, pady=2)
        self.lname.grid(row=1, column=1, padx=2, pady=2)
        self.email.grid(row=2, column=1, padx=2, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=5, padx=5)

        ttk.Button(btn_frame, text="Dodaj klienta", command=self.add_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj klienta", command=self.edit_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń klienta", command=self.delete_customer).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Odśwież", command=self.load_customers).pack(side="left", padx=5)

        self.all_customers = []
        self.load_customers()

    def load_customers(self):
        self.all_customers = Customer.get_all()
        self.display_customers(self.all_customers)

    def display_customers(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in data:
            self.tree.insert("", "end", values=(c[0], c[1], c[2], c[3]))

    def filter_customers(self, *args):
        search = self.search_var.get().lower()
        filtered = [c for c in self.all_customers if search in c[1].lower() or search in c[2].lower() or search in c[3].lower()]
        self.display_customers(filtered)

    def valid_email(self, email):
        # Prosta walidacja email regex
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def add_customer(self):
        fname, lname, email = self.fname.get().strip(), self.lname.get().strip(), self.email.get().strip()
        if not fname or not lname or not email:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
            return
        if not self.valid_email(email):
            messagebox.showwarning("Błąd", "Podaj poprawny adres email")
            return
        Customer.add(fname, lname, email)
        self.load_customers()
        self.fname.delete(0, tk.END)
        self.lname.delete(0, tk.END)
        self.email.delete(0, tk.END)

    def get_selected_customer(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Wybierz klienta z listy")
            return None
        item = self.tree.item(sel[0])
        return item["values"]

    def edit_customer(self):
        selected = self.get_selected_customer()
        if not selected:
            return
        # Pobierz dane aktualne
        cid, fname, lname, email = selected

        # Pytaj o nowe wartości
        new_fname = simpledialog.askstring("Edytuj klienta", "Imię:", initialvalue=fname)
        if new_fname is None: return
        new_lname = simpledialog.askstring("Edytuj klienta", "Nazwisko:", initialvalue=lname)
        if new_lname is None: return
        new_email = simpledialog.askstring("Edytuj klienta", "Email:", initialvalue=email)
        if new_email is None or not self.valid_email(new_email):
            messagebox.showwarning("Błąd", "Podaj poprawny adres email")
            return

        # Aktualizacja w bazie
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE customers SET first_name=%s, last_name=%s, email=%s WHERE customer_id=%s",
                           (new_fname, new_lname, new_email, cid))
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



