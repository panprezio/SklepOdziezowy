import tkinter as tk
from tkinter import ttk

def show_help_window(parent):
    help_window = tk.Toplevel(parent)
    help_window.title("Pomoc")
    help_window.geometry("600x500")
    help_window.transient(parent)


    container = ttk.Frame(help_window)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(container, borderwidth=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    def add_section(title, content):
        ttk.Label(scrollable_frame, text=title, font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Label(scrollable_frame, text=content, wraplength=550, justify="left").pack(anchor="w", padx=(10, 0))


    add_section("👤 Klienci",
                "Tutaj możesz zarządzać danymi klientów – dodawać nowych, edytować istniejących lub usuwać.")
    add_section("📦 Zarządzanie produktami",
        "Możesz przeglądać, dodawać, edytować i usuwać produkty. Wprowadź nazwę, kategorię, markę i warianty.")
    add_section("🛒 Zamówienia",
        "Możesz tworzyć nowe zamówienia, przypisywać produkty do klientów, ustalać ilości i ceny.")
    add_section("💳 Płatności",
                "Moduł płatności pozwala zarządzać płatnościami związanymi z zamówieniami – dodawać, przeglądać i usuwać.")
    add_section("💰 Statystyki",
        "Sekcja statystyk pokazuje liczbę klientów, zamówień oraz łączny przychód Twojego sklepu.")
    add_section("🧭 Nawigacja",
        "Użyj menu górnego lub przycisków nawigacyjnych, aby poruszać się między modułami aplikacji.")
    add_section("🔠 Sortowanie danych",
                "Kliknij nagłówek dowolnej kolumny w tabeli, aby posortować dane alfabetycznie według tej kolumny. "
                "Kolejne kliknięcie odwróci kolejność sortowania.")

    add_section("ℹ️ O aplikacji",
        "To jest aplikacja sklepu odzieżowego do zarządzania produktami, zamówieniami, klientami i statystykami.")


    ttk.Button(help_window, text="Zamknij", command=help_window.destroy).pack(pady=10)

