import tkinter as tk
from tkinter import ttk
import requests
from requests import HTTPError
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *

_FONT = ("Ariel", 14)
_PADDING = (50, 50, 50, 50)
STOCKS_API = "D7HDSALBHB14R8FS"
NEWS_API = "f8a3f274629f45bda555ea0e69352f15"
TWILLIO_API = ""

try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
    print("Font DPI updated successfully!")
except:
    pass


class TickerError(ValueError):
    pass


class GUI:
    def __init__(self):
        self.stock_name = None
        self.prices = None
        self.data = None
        self.low = None
        self.high = None
        self.close = None
        self.open = None
        self.dates = None
        self.stocks_data = None
        self.ticker_found = None

        self.root = tk.Tk()
        self.root.config(pady=50, padx=50, bg='white')
        self.root.title("Stocks Watcher v1.0")

        _STYLE = ttk.Style()
        _STYLE.configure('my.TButton', font=_FONT)
        s = ttk.Style()
        # Create style used by default for all Frames
        s.configure('TFrame', background='white')
        s.configure('Frame1.TFrame', background='white')

        ui_frame = ttk.Frame(self.root, padding=_PADDING, style='Frame1.TFrame')
        ui_frame.grid(row=1, column=0)

        ticker_label = ttk.Label(ui_frame, text="Ticker Name:", font=_FONT, padding=_PADDING, background='white')
        ticker_label.grid(row=0, column=0)

        self.ticker_text = tk.StringVar()
        ticker_entry = ttk.Entry(ui_frame, font=_FONT, textvariable=self.ticker_text)
        ticker_entry.focus()
        ticker_entry.grid(row=0, column=1, padx=_PADDING[0])

        search_button = ttk.Button(ui_frame, text="Search", command=self.find_ticker, style='my.TButton')
        search_button.grid(row=0, column=2)

        # sms_button = ttk.Button(ui_frame, text="SMS Updates", command=self.find_ticker, style='my.TButton')
        # sms_button.grid(row=1, column=0)
        #
        # news_button = ttk.Button(ui_frame, text="News Updates", command=self.find_ticker, style='my.TButton')
        # news_button.grid(row=1, column=2)

        # self.canvas = Canvas(self.gui_frame, width=2400, height=900, bg="white")
        #
        # self.canvas.grid(row=0, column=0)

        self.root.mainloop()

    def find_ticker(self):
        self.stock_name = self.ticker_text.get().upper()
        STOCKS_URL = "https://www.alphavantage.co/query"
        parameters = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.stock_name,
            'outputsize': 'compact',
            'apikey': STOCKS_API
        }
        try:
            stocks_response = requests.get(STOCKS_URL, params=parameters)
            # print(location_response.json())
            stocks_response.raise_for_status()
            self.stocks_data = stocks_response.json()
            try:
                if list(self.stocks_data.keys())[0] == 'Error Message':
                    raise TickerError
            except TickerError:
                messagebox.showerror(title="Stocks Watcher", message=f"Ticker {self.stock_name} not found!")
            else:
                self.ticker_found = True
                self.process_data()
        except ConnectionError:
            print('connection error')
            messagebox.showerror(title="Stocks Watcher", message="Connection Error!")
        except HTTPError:
            messagebox.showerror(title="Stocks Watcher", message="404 Error")
        print(self.stocks_data)

    def process_data(self):
        self.dates = [value for value in list(self.stocks_data['Time Series (Daily)'].keys())][::-1]
        self.open = list(pd.DataFrame(self.stocks_data['Time Series (Daily)']).loc['1. open'][::-1].astype(float))
        self.close = list(pd.DataFrame(self.stocks_data['Time Series (Daily)']).loc['4. close'][::-1].astype(float))
        self.high = list(pd.DataFrame(self.stocks_data['Time Series (Daily)']).loc['2. high'][::-1].astype(float))
        self.low = list(pd.DataFrame(self.stocks_data['Time Series (Daily)']).loc['3. low'][::-1].astype(float))
        self.data = list(zip(self.open, self.close, self.high, self.low))
        self.prices = pd.DataFrame(columns=['open', 'close', 'high', 'low'], data=self.data, index=self.dates)

        # display DataFrame
        # print(self.prices)
        plt.figure(figsize=(30, 10))

        # define width of candlestick elements
        width = .2
        width2 = .02

        # define up and down prices
        up = self.prices[self.prices.close >= self.prices.open]
        down = self.prices[self.prices.close < self.prices.open]

        # define colors to use
        col1 = 'black'
        col2 = 'black'

        # plot up prices
        plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
        plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
        plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

        # plot down prices
        plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
        plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
        plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)
        # rotate x-axis tick labels
        plt.title(f'{self.stock_name} Prices', fontsize=20)
        plt.xticks(rotation=90, ha='right', fontsize=11)
        plt.savefig("stock_figure.png", bbox_inches='tight', dpi=100)
        print('done creating pic')
        # display candlestick chart
        self.print_stocks()

    def print_stocks(self):
        self.root.destroy()
        root = tk.Tk()
        root.config(pady=50, padx=50, bg='white')
        root.title("Stocks Watcher v1.0")
        print('here')
        s = ttk.Style()
        # Create style used by default for all Frames
        s.configure('TFrame', background='white')
        s.configure('Frame1.TFrame', background='white')

        stock_picture = PhotoImage(file="./stock_figure.png")
        canvas = Canvas(width=2400, height=900)
        stock_fig = canvas.create_image(1200, 450, image=stock_picture)
        canvas.itemconfig(stock_fig, image=stock_picture)
        canvas.grid(row=0, column=0)

        ui_frame = ttk.Frame(root, padding=_PADDING, style='Frame1.TFrame')
        ui_frame.grid(row=1, column=0)
        sms_button = ttk.Button(ui_frame, text="SMS Updates", command=self.find_ticker, style='my.TButton')
        sms_button.grid(row=1, column=0)

        news_button = ttk.Button(ui_frame, text="News Updates", command=self.find_ticker, style='my.TButton')
        news_button.grid(row=1, column=2)

        root.mainloop()
