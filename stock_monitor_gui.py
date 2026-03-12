import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime


class StockMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BuzzBear")
        self.root.geometry("600x700")
        self.root.resizable(True, True)

        # Load environment variables
        load_dotenv()

        # Configuration variables
        self.stock_name = tk.StringVar(value="TSLA")
        self.company_name = tk.StringVar(value="Tesla Inc")
        self.threshold = tk.DoubleVar(value=5.0)
        self.articles_limit = tk.IntVar(value=3)

        # API endpoints
        self.STOCK_ENDPOINT = "https://www.alphavantage.co/query"
        self.NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Stock Price Monitor", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        config_frame.columnconfigure(1, weight=1)

        # Stock symbol
        ttk.Label(config_frame, text="Stock Symbol:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        stock_entry = ttk.Entry(config_frame, textvariable=self.stock_name, width=15)
        stock_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Company name
        ttk.Label(config_frame, text="Company Name:").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 5)
        )
        company_entry = ttk.Entry(
            config_frame, textvariable=self.company_name, width=20
        )
        company_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # Threshold
        ttk.Label(config_frame, text="Alert Threshold (%):").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0)
        )
        threshold_entry = ttk.Entry(config_frame, textvariable=self.threshold, width=10)
        threshold_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # Articles limit
        ttk.Label(config_frame, text="Max Articles:").grid(
            row=1, column=2, sticky=tk.W, padx=(10, 5), pady=(10, 0)
        )
        articles_spin = ttk.Spinbox(
            config_frame, from_=1, to=10, textvariable=self.articles_limit, width=5
        )
        articles_spin.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.check_button = ttk.Button(
            button_frame, text="Check Stock Price", command=self.start_check_thread
        )
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = ttk.Button(
            button_frame, text="Clear Log", command=self.clear_log
        )
        self.clear_button.pack(side=tk.LEFT)

        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
        status_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        status_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(
            status_frame, text="Ready to check stock price", font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # Price info frame
        self.price_frame = ttk.Frame(status_frame)
        self.price_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        self.price_info = ttk.Label(
            self.price_frame, text="", font=("Arial", 12, "bold")
        )
        self.price_info.pack()

        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def log_message(self, message):
        """Add a timestamped message to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the activity log"""
        self.log_text.delete(1.0, tk.END)

    def start_check_thread(self):
        """Start the stock check in a separate thread to prevent GUI freezing"""
        self.check_button.config(state="disabled")
        thread = threading.Thread(target=self.check_stock_price, daemon=True)
        thread.start()

    def check_stock_price(self):
        """Core functionality from the original script"""
        try:
            self.status_label.config(text="Checking stock price...")
            self.log_message(f"Starting stock check for {self.stock_name.get()}")

            # Prepare stock API parameters
            stock_params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": self.stock_name.get(),
                "apikey": os.environ.get("STOCK_API_KEY"),
            }

            # Get stock data
            self.log_message("Fetching stock data from Alpha Vantage...")
            response = requests.get(self.STOCK_ENDPOINT, params=stock_params)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                raise Exception(f"Stock API Error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Stock API Limit: {data['Note']}")

            time_series = data["Time Series (Daily)"]
            data_list = [value for (key, value) in time_series.items()]

            # Calculate price difference (original logic)
            yesterday_data = data_list[0]
            yesterday_closing_price = yesterday_data["4. close"]

            day_before_yesterday_data = data_list[1]
            day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

            difference = float(yesterday_closing_price) - float(
                day_before_yesterday_closing_price
            )
            up_down = "🔺" if difference > 0 else "🔻"

            difference_percent = round(
                (difference / float(yesterday_closing_price)) * 100, 2
            )

            # Update price display
            price_text = f"{self.stock_name.get()}: {up_down} {abs(difference_percent)}% (${yesterday_closing_price})"
            self.price_info.config(text=price_text)

            self.log_message(f"Price change: {difference_percent}% (${difference:.2f})")

            # Check if threshold is met
            if abs(difference_percent) > self.threshold.get():
                self.log_message("Threshold exceeded! Getting news articles...")
                self.status_label.config(text="Threshold exceeded - fetching news...")

                # Get news articles
                news_params = {
                    "apiKey": os.environ.get("NEWS_API_KEY"),
                    "q": self.company_name.get(),
                }

                news_response = requests.get(self.NEWS_ENDPOINT, params=news_params)
                news_response.raise_for_status()
                articles = news_response.json()["articles"]
                three_articles = articles[: self.articles_limit.get()]

                # Format articles (original logic)
                formatted_articles = [
                    f"{self.stock_name.get()}: {up_down}{difference_percent}% \nHeadline: {article['title']} \nBrief: {article['description']}"
                    for article in three_articles
                ]

                # Send SMS messages (original logic)
                self.log_message("Sending SMS notifications...")
                client = Client(
                    os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
                )

                for i, article in enumerate(formatted_articles, 1):
                    try:
                        message = client.messages.create(
                            body=article,
                            from_=os.environ.get("TWILIO_PHONE_NUMBER"),
                            to=os.environ.get("MY_PHONE_NUMBER"),
                        )
                        self.log_message(
                            f"SMS {i} sent - ID: {message.sid}, Status: {message.status}"
                        )
                    except Exception as sms_error:
                        self.log_message(f"Failed to send SMS {i}: {str(sms_error)}")

                self.status_label.config(
                    text=f"Alert sent! {len(formatted_articles)} SMS messages sent."
                )

            else:
                self.log_message(
                    f"No alert needed - change {abs(difference_percent)}% is below threshold {self.threshold.get()}%"
                )
                self.status_label.config(
                    text=f"No alert needed - change below {self.threshold.get()}% threshold"
                )

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.status_label.config(text="Error occurred - check log")
            messagebox.showerror("Network Error", error_msg)

        except KeyError as e:
            error_msg = f"Data format error: Missing key {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.status_label.config(text="Error occurred - check log")
            messagebox.showerror("Data Error", error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.status_label.config(text="Error occurred - check log")
            messagebox.showerror("Error", error_msg)

        finally:
            self.check_button.config(state="normal")


def main():
    # Check for required environment variables
    required_vars = [
        "STOCK_API_KEY",
        "NEWS_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "MY_PHONE_NUMBER",
    ]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "Configuration Error",
            "Missing environment variables in .env file:\n"
            + "\n".join(f"• {var}" for var in missing_vars),
        )
        return

    # Configure output encoding for Chinese characters
    sys.stdout.reconfigure(encoding="utf-8")

    root = tk.Tk()
    StockMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
