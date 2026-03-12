import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from dotenv import load_dotenv

# Import business logic service
from stock_service import StockAlertService


class StockMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BuzzBear | Enterprise Monitor")
        self.root.geometry("650x750")
        self.root.resizable(True, True)

        # Apply Corporate UI/UX Theme
        self.apply_corporate_theme()

        # Configuration variables
        self.stock_name = tk.StringVar(value="TSLA")
        self.company_name = tk.StringVar(value="Tesla Inc")
        self.threshold = tk.DoubleVar(value=5.0)
        self.articles_limit = tk.IntVar(value=3)

        self.setup_ui()

    def apply_corporate_theme(self):
        """Sets up a flat, modern corporate color palette and typography."""
        self.style = ttk.Style(self.root)
        # 'clam' theme allows for flat, modern styling across all OS platforms
        self.style.theme_use("clam")

        # Enterprise Color Palette
        self.colors = {
            "bg": "#F4F5F7",  # Light gray background
            "surface": "#FFFFFF",  # Clean white panels
            "primary": "#0052CC",  # Trustworthy Corporate Blue
            "primary_hover": "#0747A6",  # Darker blue for interactions
            "text_main": "#172B4D",  # Deep slate for primary text
            "text_muted": "#6B778C",  # Lighter gray for secondary text
            "border": "#DFE1E6",  # Subtle borders
            "success": "#00875A",  # Profit green
            "danger": "#DE350B",  # Loss red
        }

        self.root.configure(bg=self.colors["bg"])
        default_font = ("Segoe UI", 10)

        # Base Frame Styling
        self.style.configure("TFrame", background=self.colors["bg"])

        # Label Styling
        self.style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text_main"],
            font=default_font,
        )
        self.style.configure(
            "Header.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground=self.colors["text_main"],
        )
        self.style.configure(
            "Subheader.TLabel",
            font=("Segoe UI", 10),
            foreground=self.colors["text_muted"],
        )
        self.style.configure(
            "Surface.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text_main"],
            font=default_font,
        )

        # LabelFrame (Dashboard Cards)
        self.style.configure(
            "TLabelframe",
            background=self.colors["surface"],
            bordercolor=self.colors["border"],
            borderwidth=1,
        )
        self.style.configure(
            "TLabelframe.Label",
            background=self.colors["surface"],
            foreground=self.colors["primary"],
            font=("Segoe UI", 10, "bold"),
        )

        # Primary Action Button
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["primary"],
            foreground="white",
            borderwidth=0,
            padding=6,
        )
        self.style.map(
            "Primary.TButton", background=[("active", self.colors["primary_hover"])]
        )

        # Secondary Action Button
        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            background=self.colors["bg"],
            foreground=self.colors["text_main"],
            bordercolor=self.colors["border"],
            borderwidth=1,
            padding=6,
        )
        self.style.map(
            "Secondary.TButton", background=[("active", self.colors["border"])]
        )

        # Inputs
        self.style.configure(
            "TEntry",
            fieldbackground=self.colors["surface"],
            bordercolor=self.colors["border"],
            padding=4,
        )
        self.style.configure(
            "TSpinbox",
            fieldbackground=self.colors["surface"],
            bordercolor=self.colors["border"],
            padding=4,
        )

    def setup_ui(self):
        # Main Container with extra padding for whitespace
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Header Section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))
        ttk.Label(header_frame, text="BuzzBear", style="Header.TLabel").pack(
            anchor=tk.W
        )
        ttk.Label(
            header_frame,
            text="Automated Market Intelligence & Alerting",
            style="Subheader.TLabel",
        ).pack(anchor=tk.W)

        # Configuration Card
        config_frame = ttk.LabelFrame(
            main_frame, text=" Monitor Configuration ", padding="15"
        )
        config_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)

        # Row 1 Inputs
        ttk.Label(config_frame, text="Ticker Symbol:", style="Surface.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        stock_entry = ttk.Entry(config_frame, textvariable=self.stock_name, width=15)
        stock_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=(0, 10))

        ttk.Label(config_frame, text="Entity Name:", style="Surface.TLabel").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        company_entry = ttk.Entry(
            config_frame, textvariable=self.company_name, width=25
        )
        company_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Row 2 Inputs
        ttk.Label(
            config_frame, text="Variance Threshold (%):", style="Surface.TLabel"
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        threshold_entry = ttk.Entry(config_frame, textvariable=self.threshold, width=15)
        threshold_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Label(
            config_frame, text="News Article Limit:", style="Surface.TLabel"
        ).grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        articles_spin = ttk.Spinbox(
            config_frame, from_=1, to=10, textvariable=self.articles_limit, width=8
        )
        articles_spin.grid(row=1, column=3, sticky=tk.W)

        # Control Panel
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(5, 15), sticky=tk.W)

        self.check_button = ttk.Button(
            button_frame,
            text="Execute Market Check",
            style="Primary.TButton",
            command=self.start_check_thread,
        )
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = ttk.Button(
            button_frame,
            text="Clear System Log",
            style="Secondary.TButton",
            command=self.clear_log,
        )
        self.clear_button.pack(side=tk.LEFT)

        # Status & Telemetry Card
        status_frame = ttk.LabelFrame(main_frame, text=" Live Telemetry ", padding="15")
        status_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        status_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(
            status_frame,
            text="System idle. Awaiting execution command.",
            style="Surface.TLabel",
        )
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self.price_frame = ttk.Frame(status_frame, style="Surface.TFrame")
        self.price_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        self.price_info = ttk.Label(
            self.price_frame,
            text="",
            style="Surface.TLabel",
            font=("Segoe UI", 16, "bold"),
        )
        self.price_info.pack(anchor=tk.W)

        # System Log Card
        log_frame = ttk.LabelFrame(main_frame, text=" Execution Log ", padding="15")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Style the ScrolledText to match the flat corporate look
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            wrap=tk.WORD,
            bg=self.colors["surface"],
            fg=self.colors["text_main"],
            font=("Consolas", 9),
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"],
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def log_message(self, message):
        """Add a timestamped message to the log"""
        # Import datetime locally here to keep the global namespace clean
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the activity log"""
        self.log_text.delete(1.0, tk.END)

    def start_check_thread(self):
        """Start the stock check in a separate thread"""
        self.check_button.config(state="disabled")
        thread = threading.Thread(target=self.check_stock_price, daemon=True)
        thread.start()

    def check_stock_price(self):
        """Delegates business logic to the StockAlertService"""
        try:
            self.status_label.config(
                text="Status: Connecting to financial data APIs..."
            )
            self.log_message(
                f"Initiating market check for ticker: {self.stock_name.get()}"
            )

            service = StockAlertService(
                stock_symbol=self.stock_name.get(),
                company_name=self.company_name.get(),
                threshold=self.threshold.get(),
                articles_limit=self.articles_limit.get(),
            )

            self.log_message("Querying Alpha Vantage endpoint...")
            diff_percent, trend, current_price = service.check_price_change()

            # Dynamic Corporate Coloring for the Price Trend
            trend_color = (
                self.colors["success"] if diff_percent > 0 else self.colors["danger"]
            )
            price_text = f"{self.stock_name.get()} {trend} {abs(diff_percent)}% (Closing: ${current_price})"
            self.price_info.config(text=price_text, foreground=trend_color)

            self.log_message(f"Calculated variance: {trend} {abs(diff_percent)}%")

            if abs(diff_percent) > self.threshold.get():
                self.log_message(
                    f"Variance exceeds {self.threshold.get()}% threshold. Fetching market context..."
                )
                self.status_label.config(
                    text="Status: Threshold breached. Aggregating news articles..."
                )

                articles = service.fetch_news()
                self.log_message(
                    f"Sourced {len(articles)} relevant articles. Dispatching payload via Twilio..."
                )

                service.send_sms_alerts(articles, diff_percent, trend)

                self.status_label.config(
                    text=f"Status: Alert dispatched successfully. ({len(articles)} messages)"
                )
                self.log_message("Execution cycle complete.")
            else:
                self.log_message(
                    f"Variance within acceptable parameters (<{self.threshold.get()}%)."
                )
                self.status_label.config(
                    text="Status: Variance nominal. No alerts dispatched."
                )

        except ValueError as e:
            # Handles our custom API limit/error messages from the service
            error_msg = str(e)
            self.log_message(f"CRITICAL DATA FAULT: {error_msg}")
            self.status_label.config(text="Status: Data retrieval failed. See log.")
            messagebox.showerror("Data Fault", error_msg)

        except Exception as e:
            # Catch-all for network issues or unexpected Twilio errors
            error_msg = f"Unhandled exception: {str(e)}"
            self.log_message(f"SYSTEM ERROR: {error_msg}")
            self.status_label.config(text="Status: System failure. See log.")
            messagebox.showerror("System Error", error_msg)

        finally:
            self.check_button.config(state="normal")


def main():
    # Load environment variables
    load_dotenv()

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
        root.withdraw()
        messagebox.showerror(
            "Environment Configuration Fault",
            "Missing parameters in .env file:\n"
            + "\n".join(f"• {var}" for var in missing_vars),
        )
        return

    # Configure output encoding for Chinese characters/Emojis
    sys.stdout.reconfigure(encoding="utf-8")

    root = tk.Tk()
    StockMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
