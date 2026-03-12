import sys
from dotenv import load_dotenv
from stock_service import StockAlertService

# Fixes output encoding for specific console environments
sys.stdout.reconfigure(encoding="utf-8")

def main():
    load_dotenv()
    
    # Configuration
    STOCK_NAME = "TSLA"
    COMPANY_NAME = "Tesla Inc"
    THRESHOLD = 5.0

    print(f"Starting stock monitor for {COMPANY_NAME} ({STOCK_NAME})...")
    
    service = StockAlertService(
        stock_symbol=STOCK_NAME, 
        company_name=COMPANY_NAME, 
        threshold=THRESHOLD
    )
    
    service.run_monitor()

if __name__ == "__main__":
    main()