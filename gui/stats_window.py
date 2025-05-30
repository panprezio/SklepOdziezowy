import tkinter as tk
from tkinter import ttk
from db.db import connect

class StatsFrame(tk.Frame):
    def __init__(self, master, controller=None):
        super().__init__(master)

        # Załaduj statystyki
        total_customers = self.count("SELECT COUNT(*) FROM customers")
        total_orders = self.count("SELECT COUNT(*) FROM orders")
        total_revenue = self.count("SELECT SUM(total_price) FROM orders")


        stats_frame = ttk.Frame(self)
        stats_frame.pack(pady=20, padx=20)

        ttk.Label(stats_frame, text=f"Liczba klientów: {total_customers}", font=("Arial", 14)).pack(pady=5)
        ttk.Label(stats_frame, text=f"Liczba zamówień: {total_orders}", font=("Arial", 14)).pack(pady=5)
        ttk.Label(stats_frame, text=f"Łączny przychód: {total_revenue if total_revenue else 0} zł", font=("Arial", 14)).pack(pady=5)

    def count(self, query):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
