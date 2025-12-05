from kiteconnect import KiteConnect, KiteTicker
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class KiteIntegration:
    def __init__(self):
        self.api_key = os.getenv('ZERODHA_API_KEY')
        self.api_secret = os.getenv('ZERODHA_API_SECRET')
        self.access_token = os.getenv('ZERODHA_ACCESS_TOKEN')

        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)

        # Initialize KiteTicker for live data
        self.kws = KiteTicker(self.api_key, self.access_token)

    def get_login_url(self):
        """Generate login URL for Zerodha authentication"""
        return self.kite.login_url()

    def generate_session(self, request_token):
        """Generate access token from request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.kite.set_access_token(data["access_token"])
            return data
        except Exception as e:
            logger.error(f"Error generating session: {str(e)}")
            raise

    def get_instruments(self, exchange="NSE"):
        """Get list of instruments for an exchange"""
        try:
            return self.kite.instruments(exchange=exchange)
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise

    def get_quote(self, instrument_token):
        """Get live quote for an instrument"""
        try:
            return self.kite.quote(instrument_token=instrument_token)
        except Exception as e:
            logger.error(f"Error fetching quote: {str(e)}")
            raise

    def get_historical_data(self, instrument_token, from_date, to_date, interval="day"):
        """Get historical data for an instrument"""
        try:
            return self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, order_type, quantity, price=None, trigger_price=None):
        """Place an order"""
        try:
            order_params = {
                "variety": variety,
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": transaction_type,
                "order_type": order_type,
                "quantity": quantity,
            }
            if price:
                order_params["price"] = price
            if trigger_price:
                order_params["trigger_price"] = trigger_price

            return self.kite.place_order(**order_params)
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise

    def get_orders(self):
        """Get list of orders"""
        try:
            return self.kite.orders()
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise

    def get_positions(self):
        """Get current positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            raise
