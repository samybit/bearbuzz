import os
import requests
from typing import List, Tuple
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class StockAlertService:
    STOCK_ENDPOINT = "https://www.alphavantage.co/query"
    NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

    def __init__(self, stock_symbol: str, company_name: str, threshold: float = 5.0, articles_limit: int = 3):
        self.stock_symbol = stock_symbol
        self.company_name = company_name
        self.threshold = threshold
        self.articles_limit = articles_limit
        
        # Keys
        self.stock_api_key = os.environ.get("STOCK_API_KEY")
        self.news_api_key = os.environ.get("NEWS_API_KEY")
        self.twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.environ.get("TWILIO_PHONE_NUMBER")
        self.twilio_to = os.environ.get("MY_PHONE_NUMBER")

    def check_price_change(self) -> Tuple[float, str, float]:
        """Returns difference percentage, trend symbol, and latest price."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": self.stock_symbol,
            "apikey": self.stock_api_key,
        }

        response = requests.get(self.STOCK_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data or "Note" in data:
            raise ValueError(f"AlphaVantage API Error/Limit: {data.get('Error Message') or data.get('Note')}")

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            raise ValueError("Time series data missing from response.")

        # Extract the last two days
        data_list = list(time_series.values())
        yesterday_close = float(data_list[0]["4. close"])
        day_before_close = float(data_list[1]["4. close"])

        difference = yesterday_close - day_before_close
        trend = "🔺" if difference > 0 else "🔻"
        diff_percent = round((difference / yesterday_close) * 100, 2)

        return diff_percent, trend, yesterday_close

    def fetch_news(self) -> List[dict]:
        """Fetches latest news articles for the company."""
        params = {
            "apiKey": self.news_api_key,
            "q": self.company_name,
            "pageSize": self.articles_limit
        }
        response = requests.get(self.NEWS_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json().get("articles", [])

    def send_sms_alerts(self, articles: List[dict], diff_percent: float, trend: str) -> None:
        """Formats articles and sends SMS alerts via Twilio."""
        if not articles:
            return

        client = Client(self.twilio_account_sid, self.twilio_token)
        
        for article in articles:
            body = (
                f"{self.stock_symbol}: {trend}{abs(diff_percent)}%\n"
                f"Headline: {article.get('title')}\n"
                f"Brief: {article.get('description')}"
            )
            try:
                message = client.messages.create(
                    body=body,
                    from_=self.twilio_from,
                    to=self.twilio_to,
                )
                print(f"Alert sent successfully: SID {message.sid}")
            except TwilioRestException as e:
                print(f"Failed to send SMS: {e}")

    def run_monitor(self) -> None:
        """Main execution flow."""
        try:
            diff_percent, trend, current_price = self.check_price_change()
            print(f"{self.stock_symbol} moved {trend} {abs(diff_percent)}% (Current: ${current_price})")

            if abs(diff_percent) > self.threshold:
                print(f"Threshold of {self.threshold}% exceeded. Fetching news...")
                articles = self.fetch_news()
                self.send_sms_alerts(articles, diff_percent, trend)
            else:
                print("Price change is below threshold. No alerts sent.")
                
        except requests.RequestException as e:
            print(f"Network error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")