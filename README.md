# Stock & News Alert Monitor (BuzzBear)

This Python application monitors a stock's daily price changes using the [Alpha Vantage API](https://www.alphavantage.co/). If the price moves significantly, it fetches related news from the [News API](https://newsapi.org/) and sends alerts via [Twilio SMS](https://www.twilio.com/).

It features both a lightweight Command Line Interface (CLI) and a fully featured Graphical User Interface (GUI) built with Tkinter.

---

### Features
- **Dual Interfaces:** Run seamlessly via the terminal (`main.py`) or the interactive desktop GUI (`stock_monitor_gui.py`).
- **Separation of Concerns:** Core API and communication logic is isolated in `stock_service.py` for easy testing and maintenance.
- **Automated Data Fetching:** Compares yesterday’s closing stock price with the day before.
- **Smart Alerting:** Calculates price change percentage and direction (🔺 / 🔻). If the change exceeds your custom threshold, it fetches the latest company news.
- **SMS Notifications:** Sends formatted text alerts (including news headlines and briefs) directly to your phone through Twilio.

---

### Requirements
- Python 3.9+
- The following Python packages (install via `pip install -r requirements.txt` if available, or manually install `requests`, `python-dotenv`, and `twilio`).
- A `.env` file placed in the root directory with your API keys and Twilio credentials.

**Required `.env` Configuration:**
```env
STOCK_API_KEY=your_alphavantage_key
NEWS_API_KEY=your_newsapi_key
TWILIO_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
MY_PHONE_NUMBER=the_number_to_receive_alerts
```

### Usage

Run the script:

python main.py
(By default, the CLI monitors TSLA (Tesla Inc) with a 5% threshold.)

To run the Graphical Interface (BuzzBear):

python stock_monitor_gui.py
(The GUI allows you to dynamically change the stock symbol, company name, threshold percentage, and the maximum number of news articles to fetch without editing the code.)

---

### Notes

The script uses sys.stdout.reconfigure(encoding="utf-8") to ensure emojis and special characters render correctly in terminal environments.

Stock and news APIs may have rate limits on their free tiers (e.g., Alpha Vantage typically limits free users to 25 requests per day).

Primarily tested with U.S. stock symbols.
