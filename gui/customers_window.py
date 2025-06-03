import tkinter as tk
from tkinter import ttk, messagebox
from models.customer import Customer
import re
from db.db import connect


class CustomerFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        self.tree_tag_even = "evenrow"
        self.tree_tag_odd = "oddrow"
        self.tree = None
        self.entries = {}

        self.setup_styles()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)


        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar()


        self.all_customers = []


        self.search_var.trace_add("write", self.filter_customers)
        ttk.Label(search_frame, text="Szukaj klienta:", font=("Arial", 10)).pack(side="left", padx=(5, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('TkDefaultFont', 10))

        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))


        columns = ("ID", "Imię", "Nazwisko", "Email")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)


        form = ttk.LabelFrame(main_frame)
        form.pack(fill="x", padx=10, pady=10)


        ttk.Label(form, text="Imię:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entries["imię"] = ttk.Entry(form, font=("Arial", 11))
        self.entries["imię"].grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.entries["imię"], "np. Jan")


        ttk.Label(form, text="Nazwisko:", font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entries["nazwisko"] = ttk.Entry(form, font=("Arial", 11))
        self.entries["nazwisko"].grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.entries["nazwisko"], "np. Kowalski")


        ttk.Label(form, text="Email:", font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entries["email"] = ttk.Entry(form, font=("Arial", 11))
        self.entries["email"].grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.add_placeholder(self.entries["email"], "np. jan.kowalski@example.com")

        form.columnconfigure(1, weight=1)


        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(button_frame, text="Dodaj", command=self.add_customer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edytuj", command=self.edit_customer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Usuń", command=self.delete_customer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Odśwież", command=self.load_customers).pack(side="left", padx=5)

        self.all_customers = []
        self.load_customers()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('TkDefaultFont', 10))
        style.configure("Treeview.Heading", font=('TkDefaultFont', 10, 'bold'))
        style.map("Treeview", background=[("selected", "#ececec")])

    def add_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(foreground="gray")

        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, text)
                entry.config(foreground="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

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
        self.tree.tag_configure(self.tree_tag_even, background="#f2f2f2")
        self.tree.tag_configure(self.tree_tag_odd, background="#ffffff")

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

        edit_win = tk.Toplevel(self)
        edit_win.title("Edytuj klienta")
        edit_win.grab_set()
        edit_win.resizable(False, False)

        ttk.Label(edit_win, text="Imię:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        fname_entry = ttk.Entry(edit_win, width=30)
        fname_entry.insert(0, fname)
        fname_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Nazwisko:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        lname_entry = ttk.Entry(edit_win, width=30)
        lname_entry.insert(0, lname)
        lname_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(edit_win, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        email_entry = ttk.Entry(edit_win, width=30)
        email_entry.insert(0, email)
        email_entry.grid(row=2, column=1, padx=10, pady=5)

        def save_changes():
            new_fname = fname_entry.get().strip()
            new_lname = lname_entry.get().strip()
            new_email = email_entry.get().strip()

            if not new_fname or not new_lname or not new_email:
                messagebox.showwarning("Błąd", "Wszystkie pola muszą być wypełnione")
                return

            if not self.valid_email(new_email):
                messagebox.showwarning("Błąd", "Podaj poprawny adres email")
                return

            try:
                conn = connect()
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id = %s", (cid,))
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Błąd", "Klient nie istnieje.")
                    conn.close()
                    edit_win.destroy()
                    return

                cursor.execute("SELECT COUNT(*) FROM customers WHERE email = %s AND customer_id != %s",
                               (new_email, cid))
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
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")


        ttk.Button(edit_win, text="Zapisz zmiany", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

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







