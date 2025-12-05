# Stock Market Analysis Tool

A comprehensive stock market analysis tool focused on Sensex, Nifty, and BankNifty indices. This project provides real-time market analysis, options chain analysis, and automated trading signal generation with Zerodha API integration.

## Features

### Core Functionality
- **Live Market Data**: Real-time price feeds for Sensex, Nifty, and BankNifty
- **Options Analysis**: Comprehensive F&O (Futures & Options) analysis including:
  - Option chain data retrieval
  - Open interest analysis
  - Put-Call ratio calculations
  - Strike price recommendations
- **Signal Generation**: Automated trading signals based on:
  - Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
  - Candlestick patterns (Doji, Hammer, Engulfing, Morning Star)
  - Market direction analysis
- **Risk Management**: Built-in stop-loss and profit booking logic
- **Profit Maximization**: Conservative trading strategies focused on minimizing losses

### Technical Features
- **Zerodha API Integration**: Seamless integration with Kite API for live data and order execution
- **Real-time Updates**: Live market data streaming and analysis
- **Historical Data Analysis**: 60-day historical data for technical analysis
- **Web Interface**: User-friendly frontend for monitoring and trading

## Project Structure

```
stock-market-analysis/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── kite_integration.py    # Zerodha API integration
│   ├── signal_generator.py    # Trading signal generation
│   ├── option_analyzer.py     # Options chain analysis
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/
│   ├── index.html            # Main dashboard
│   ├── css/
│   │   └── styles.css        # Styling
│   ├── js/
│   │   └── app.js           # Frontend logic
│   └── assets/               # Images and icons
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Zerodha trading account with API access
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-market-analysis
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Zerodha API**
   - Copy `.env.example` to `.env`
   - Fill in your Zerodha API credentials:
     ```
     ZERODHA_API_KEY=your_api_key_here
     ZERODHA_API_SECRET=your_api_secret_here
     ZERODHA_ACCESS_TOKEN=your_access_token_here
     ```

5. **Run the backend server**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Open index.html in your browser**
   - Or serve it using a local server:
   ```bash
   python -m http.server 8000
   ```

## API Endpoints

### Market Data
- `GET /market_data/<symbol>` - Get live market data for a symbol
- `GET /signals/<symbol>` - Get trading signals for a symbol
- `GET /option_chain/<symbol>` - Get options chain data
- `GET /option_analysis/<symbol>` - Get comprehensive options analysis

### Supported Symbols
- NIFTY (Nifty 50)
- BANKNIFTY (Bank Nifty)
- SENSEX (BSE Sensex)

## Usage

### Getting Trading Signals
```python
import requests

# Get signals for Nifty
response = requests.get('http://localhost:5000/signals/NIFTY')
signals = response.json()

print(f"Direction: {signals['direction']}")
print(f"Entry Price: {signals['entry_price']}")
print(f"Stop Loss: {signals['stop_loss']}")
print(f"Target: {signals['target']}")
print(f"Confidence: {signals['confidence']}")
```

### Options Analysis
```python
# Get options analysis for BankNifty
response = requests.get('http://localhost:5000/option_analysis/BANKNIFTY')
analysis = response.json()

print(f"Market Direction: {analysis['market_direction']}")
print(f"PCR: {analysis['pcr']}")
print(f"Recommended Strikes: {analysis['optimal_strikes']}")
```

## Trading Strategy

### Signal Interpretation
- **Bullish**: Price expected to go up - consider buying calls or underlying
- **Bearish**: Price expected to go down - consider buying puts
- **Neutral**: Sideways movement - consider spreads or stay out

### Risk Management
- **Stop Loss**: Automatically calculated at 2% below entry for trending markets
- **Profit Booking**: Target set at 5% above entry for trending markets
- **Position Sizing**: Conservative approach to minimize losses

### Options Strategy
- **Call Buying**: When bullish signals with high confidence
- **Put Buying**: When bearish signals with high confidence
- **Spreads**: For neutral signals to reduce risk

## Technical Indicators Used

### Trend Indicators
- Simple Moving Averages (20, 50 periods)
- Exponential Moving Averages (12, 26 periods)

### Momentum Indicators
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)

### Volatility Indicators
- Bollinger Bands
- On Balance Volume (OBV)

### Pattern Recognition
- Candlestick patterns using TA-Lib library

## Safety Features

### Conservative Approach
- Focus on profit maximization while avoiding losses
- Strict stop-loss implementation
- Confidence-based signal filtering

### Risk Controls
- Maximum loss limits per trade
- Position size restrictions
- Market hours validation

## Disclaimer

This tool is for educational and informational purposes only. Trading in financial markets involves substantial risk of loss and is not suitable for every investor. Past performance does not guarantee future results. Please consult with a qualified financial advisor before making any investment decisions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## Future Enhancements

- [ ] Machine learning-based predictions
- [ ] Advanced options strategies
- [ ] Portfolio management
- [ ] Mobile app development
- [ ] Real-time notifications
- [ ] Backtesting framework
