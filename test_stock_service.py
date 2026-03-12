import unittest
from unittest.mock import patch, MagicMock
from stock_service import StockAlertService


class TestStockAlertService(unittest.TestCase):
    def setUp(self):
        """Set up a fresh instance of the service for each test with dummy credentials."""
        self.service = StockAlertService(
            stock_symbol="TSLA",
            company_name="Tesla Inc",
            threshold=5.0,
            articles_limit=3,
        )
        # Manually inject fake keys so tests don't rely on your actual .env file
        self.service.stock_api_key = "FAKE_STOCK_KEY"
        self.service.news_api_key = "FAKE_NEWS_KEY"
        self.service.twilio_account_sid = "FAKE_SID"
        self.service.twilio_token = "FAKE_TOKEN"
        self.service.twilio_from = "+1234567890"
        self.service.twilio_to = "+0987654321"

    @patch("stock_service.requests.get")
    def test_check_price_change_success(self, mock_get):
        """Test that price differences are calculated correctly."""
        # Create a fake JSON response that mimics Alpha Vantage
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2023-10-10": {"4. close": "210.00"},  # Yesterday
                "2023-10-09": {"4. close": "200.00"},  # Day Before
            }
        }
        mock_get.return_value = mock_response

        diff_percent, trend, current_price = self.service.check_price_change()

        # 210 - 200 = 10. (10 / 210) * 100 = 4.76%
        self.assertEqual(diff_percent, 4.76)
        self.assertEqual(trend, "🔺")
        self.assertEqual(current_price, 210.00)

    @patch("stock_service.requests.get")
    def test_check_price_change_api_limit(self, mock_get):
        """Test that the service correctly raises an error if the API limit is hit."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 25 calls per day."
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.service.check_price_change()

        self.assertTrue("AlphaVantage API Error/Limit" in str(context.exception))

    @patch("stock_service.requests.get")
    def test_fetch_news_success(self, mock_get):
        """Test that news articles are parsed correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {"title": "Test Headline 1", "description": "Test Brief 1"},
                {"title": "Test Headline 2", "description": "Test Brief 2"},
            ]
        }
        mock_get.return_value = mock_response

        articles = self.service.fetch_news()

        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Test Headline 1")

    @patch("stock_service.Client")
    def test_send_sms_alerts(self, mock_twilio_client):
        """Test that Twilio client is called with the correct formatted messages."""
        # Set up the mock Twilio messages.create method
        mock_messages = MagicMock()
        mock_twilio_client.return_value.messages = mock_messages

        articles = [{"title": "Big News", "description": "Stocks go up."}]

        # Execute the function
        self.service.send_sms_alerts(articles, 5.5, "🔺")

        # Verify that Twilio's create method was called exactly once
        mock_messages.create.assert_called_once()

        # Inspect the arguments it was called with
        call_args = mock_messages.create.call_args[1]
        self.assertEqual(call_args["from_"], "+1234567890")
        self.assertEqual(call_args["to"], "+0987654321")
        self.assertIn("TSLA: 🔺5.5%", call_args["body"])
        self.assertIn("Big News", call_args["body"])


if __name__ == "__main__":
    unittest.main()
