import tkinter as tk
from tkinter import ttk
from db.db import connect
from datetime import datetime

class StatsFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)
        self.configure(padx=20, pady=20)

        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(expand=True)

        self.stat_labels = {}
        self.create_stat_labels()
        self.load_stats()

        refresh_btn = ttk.Button(self, text="Odśwież", command=self.load_stats)
        refresh_btn.pack(pady=(20, 0))

    def create_stat_labels(self):
        labels = [
            ("Liczba klientów: {}", "customers"),
            ("Liczba zamówień: {}", "orders"),
            ("Łączny przychód: {:.2f} zł", "revenue"),
            ("Średnia wartość zamówienia: {:.2f} zł", "avg_order"),
            ("Przychód w tym miesiącu: {:.2f} zł", "monthly_revenue"),
        ]

        for text_template, key in labels:
            frame = tk.Frame(self.stats_frame, bd=1, relief="solid", width=600, height=60)
            frame.pack(pady=10)
            frame.pack_propagate(False)

            label = tk.Label(
                frame,
                text="...",
                font=("Arial", 20),
                anchor="center",
                justify="center"
            )
            label.pack(expand=True, fill="both")
            self.stat_labels[key] = (label, text_template)

    def load_stats(self):
        total_customers = self.query_single("SELECT COUNT(*) FROM customers")
        total_orders = self.query_single("SELECT COUNT(*) FROM orders")
        total_revenue = self.query_single("SELECT SUM(total_price) FROM orders")
        avg_order = self.query_single("SELECT AVG(total_price) FROM orders")
        monthly_revenue = self.query_single("""
            SELECT SUM(total_price)
            FROM orders
            WHERE EXTRACT(YEAR FROM order_date) = %s AND EXTRACT(MONTH FROM order_date) = %s
        """, (datetime.now().year, datetime.now().month))

        stats = {
            "customers": total_customers,
            "orders": total_orders,
            "revenue": total_revenue or 0,
            "avg_order": avg_order or 0,
            "monthly_revenue": monthly_revenue or 0,
        }

        for key, value in stats.items():
            label, template = self.stat_labels[key]
            label.config(text=template.format(value))

    def query_single(self, query, params=()):
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()[0]
            conn.close()
            return result if result else 0
        except Exception as e:
            print(f"Błąd podczas zapytania: {e}")
            return 0




