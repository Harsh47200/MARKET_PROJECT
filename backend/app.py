from flask import Flask, jsonify, request
from kite_integration import KiteIntegration
from signal_generator import SignalGenerator
from option_analyzer import OptionAnalyzer
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize integrations
kite_integration = KiteIntegration()
signal_generator = SignalGenerator(kite_integration)
option_analyzer = OptionAnalyzer(kite_integration)

@app.route('/')
def home():
    return jsonify({"message": "Stock Market Analysis API"})

@app.route('/market_data/<symbol>')
def get_market_data(symbol):
    try:
        # Get live market data for the symbol
        instruments = kite_integration.get_instruments(exchange="NSE")
        instrument_token = None

        for instrument in instruments:
            if instrument['tradingsymbol'] == symbol:
                instrument_token = instrument['instrument_token']
                break

        if instrument_token:
            data = kite_integration.get_quote(instrument_token)
            return jsonify(data)
        else:
            return jsonify({"error": "Symbol not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/option_chain/<symbol>')
def get_option_chain(symbol):
    try:
        # Get option chain data
        options = option_analyzer.get_option_chain(symbol)
        return jsonify(options[:20])  # Return first 20 options for brevity
    except Exception as e:
        logger.error(f"Error fetching option chain: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/signals/<symbol>')
def get_signals(symbol):
    try:
        # Generate trading signals
        signal = signal_generator.generate_signal(symbol)
        return jsonify(signal)
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
