import tkinter as tk
from tkinter import messagebox, PhotoImage
from gui.customers_window import CustomerFrame
from gui.products_window import ProductFrame
from gui.orders_window import OrderFrame
from gui.stats_window import StatsFrame


icons = {}

def load_icons():
    global icons
    try:
        icons["customers"] = PhotoImage(file="gui/icons/customers.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'customers':", e)
        icons["customers"] = None
    try:
        icons["products"] = PhotoImage(file="gui/icons/products.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'products':", e)
        icons["products"] = None
    try:
        icons["orders"] = PhotoImage(file="gui/icons/orders.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'orders':", e)
        icons["orders"] = None
    try:
        icons["stats"] = PhotoImage(file="gui/icons/stats.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'stats':", e)
        icons["stats"] = None
    try:
        icons["help"] = PhotoImage(file="gui/icons/help.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'help':", e)
        icons["help"] = None
    try:
        icons["close"] = PhotoImage(file="gui/icons/close.png")
    except Exception as e:
        print("Błąd wczytywania ikony 'close':", e)
        icons["close"] = None

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sklep Odzieżowy")

        # Menu
        menu = tk.Menu(self)
        self.config(menu=menu)


        menu.add_command(label="Klienci",
                         image=icons["customers"] if icons["customers"] else None,
                         compound="left",
                         command=lambda: self.show_frame("customers"))
        menu.add_command(label="Produkty",
                         image=icons["products"] if icons["products"] else None,
                         compound="left",
                         command=lambda: self.show_frame("products"))
        menu.add_command(label="Zamówienia",
                         image=icons["orders"] if icons["orders"] else None,
                         compound="left",
                         command=lambda: self.show_frame("orders"))
        menu.add_command(label="Statystyki",
                         image=icons["stats"] if icons["stats"] else None,
                         compound="left",
                         command=lambda: self.show_frame("stats"))
        menu.add_separator()
        menu.add_command(label="Pomoc",
                         image=icons["help"] if icons["help"] else None,
                         compound="left",
                         command=self.show_help)
        menu.add_command(label="Zamknij",
                         image=icons["close"] if icons["close"] else None,
                         compound="left",
                         command=self.quit)


        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)


        self.frames = {}
        for FrameClass, name in [(CustomerFrame, "customers"),
                                 (ProductFrame, "products"),
                                 (OrderFrame, "orders"),
                                 (StatsFrame, "stats")]:
            frame = FrameClass(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame("customers")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_help(self):
        messagebox.showinfo(
            "Pomoc",
            "To jest aplikacja sklepu odzieżowego.\n"
            "Wybierz opcję z menu aby zarządzać danymi."
        )

if __name__ == "__main__":
    load_icons()
    app = MainApp()
    app.mainloop()






