import tkinter as tk
from tkinter import messagebox, PhotoImage
from gui.customers_window import CustomerFrame
from gui.products_window import ProductFrame
from gui.orders_window import OrderFrame
from gui.stats_window import StatsFrame
from gui.payments_window import PaymentsFrame
from gui.show_help import show_help_window





class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sklep Odzieżowy")
        self.state("zoomed")


        menu = tk.Menu(self)
        self.config(menu=menu)

        menu.add_command(label="Klienci",

                         compound="left",
                         command=lambda: self.show_frame("customers"))
        menu.add_command(label="Produkty",

                         compound="left",
                         command=lambda: self.show_frame("products"))
        menu.add_command(label="Zamówienia",

                         compound="left",
                         command=lambda: self.show_frame("orders"))
        menu.add_command(label="Płatności",

                         compound="left",
                         command=lambda: self.show_frame("platnosci"))
        menu.add_command(label="Statystyki",

                         compound="left",
                         command=lambda: self.show_frame("stats"))
        menu.add_separator()
        menu.add_command(label="Pomoc",

                         compound="left",
                         command=self.show_help)
        menu.add_command(label="Zamknij",

                         compound="left",
                         command=self.quit)


        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)


        self.frames = {}
        for FrameClass, name in [
            (CustomerFrame, "customers"),
            (ProductFrame, "products"),
            (OrderFrame, "orders"),
            (StatsFrame, "stats"),
            (PaymentsFrame, "platnosci")
        ]:
            frame = FrameClass(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("customers")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_help(self):
        show_help_window(self)


if __name__ == "__main__":

    app = MainApp()
    app.mainloop()







