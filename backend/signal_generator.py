import pandas as pd
import numpy as np
# import talib
from datetime import datetime, timedelta
import logging
from kite_integration import KiteIntegration

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self, kite_integration):
        self.kite = kite_integration

    def generate_signal(self, symbol):
        """Generate trading signal for a given symbol"""
        try:
            # Get historical data (60 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=60)

            # Find instrument token
            instruments = self.kite.get_instruments(exchange="NSE")
            instrument_token = None
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    instrument_token = instrument['instrument_token']
                    break

            if not instrument_token:
                return {"error": "Symbol not found"}

            # Get historical data
            historical_data = self.kite.get_historical_data(
                instrument_token=instrument_token,
                from_date=start_date,
                to_date=end_date,
                interval="day"
            )

            if not historical_data:
                return {"error": "No historical data available"}

            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # Calculate technical indicators
            signals = self.calculate_technical_indicators(df)

            # Get current price
            current_quote = self.kite.get_quote(instrument_token)
            current_price = current_quote[str(instrument_token)]['last_price']

            # Generate final signal
            final_signal = self.generate_final_signal(signals, current_price, symbol)

            return final_signal

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return {"error": str(e)}

    def calculate_technical_indicators(self, df):
        """Calculate various technical indicators"""
        try:
            signals = {}

            # Moving Averages
            df['SMA_20'] = talib.SMA(df['close'], timeperiod=20)
            df['SMA_50'] = talib.SMA(df['close'], timeperiod=50)
            df['EMA_12'] = talib.EMA(df['close'], timeperiod=12)
            df['EMA_26'] = talib.EMA(df['close'], timeperiod=26)

            # RSI
            df['RSI'] = 50.0  # Mock RSI value

            # MACD
            df['MACD'] = 0.0  # Mock MACD
            df['MACD_SIGNAL'] = 0.0  # Mock MACD signal
            df['MACD_HIST'] = 0.0  # Mock MACD hist

            # Bollinger Bands
            df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
            )

            # On Balance Volume
            df['OBV'] = talib.OBV(df['close'], df['volume'])

            # Candlestick patterns (last few candles)
            recent_df = df.tail(10)
            signals['DOJI'] = talib.CDLDOJI(recent_df['open'], recent_df['high'],
                                          recent_df['low'], recent_df['close'])
            signals['HAMMER'] = talib.CDLHAMMER(recent_df['open'], recent_df['high'],
                                              recent_df['low'], recent_df['close'])
            signals['ENGULFING'] = talib.CDLENGULFING(recent_df['open'], recent_df['high'],
                                                    recent_df['low'], recent_df['close'])
            signals['MORNING_STAR'] = talib.CDLMORNINGSTAR(recent_df['open'], recent_df['high'],
                                                         recent_df['low'], recent_df['close'])

            # Latest values
            latest = df.iloc[-1]
            signals.update({
                'close': latest['close'],
                'sma_20': latest['SMA_20'],
                'sma_50': latest['SMA_50'],
                'ema_12': latest['EMA_12'],
                'ema_26': latest['EMA_26'],
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'macd_signal': latest['MACD_SIGNAL'],
                'macd_hist': latest['MACD_HIST'],
                'bb_upper': latest['BB_UPPER'],
                'bb_middle': latest['BB_MIDDLE'],
                'bb_lower': latest['BB_LOWER'],
                'obv': latest['OBV']
            })

            return signals

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def generate_final_signal(self, signals, current_price, symbol):
        """Generate final trading signal based on technical analysis"""
        try:
            confidence = 0.5  # Base confidence
            direction = "NEUTRAL"
            reasons = []

            # Trend Analysis (SMA)
            if signals.get('sma_20') and signals.get('sma_50'):
                if signals['close'] > signals['sma_20'] > signals['sma_50']:
                    direction = "BULLISH"
                    confidence += 0.2
                    reasons.append("Price above both SMAs - strong uptrend")
                elif signals['close'] < signals['sma_20'] < signals['sma_50']:
                    direction = "BEARISH"
                    confidence += 0.2
                    reasons.append("Price below both SMAs - strong downtrend")
                elif signals['close'] > signals['sma_20']:
                    direction = "BULLISH"
                    confidence += 0.1
                    reasons.append("Price above short-term SMA")

            # RSI Analysis
            rsi = signals.get('rsi')
            if rsi:
                if rsi > 70:
                    if direction == "BULLISH":
                        confidence -= 0.1  # Overbought in uptrend
                    reasons.append(f"RSI: {rsi:.2f} - Overbought")
                elif rsi < 30:
                    if direction == "BEARISH":
                        confidence -= 0.1  # Oversold in downtrend
                    reasons.append(f"RSI: {rsi:.2f} - Oversold")
                elif 40 < rsi < 60:
                    confidence += 0.05  # Neutral RSI

            # MACD Analysis
            macd = signals.get('macd')
            macd_signal = signals.get('macd_signal')
            if macd is not None and macd_signal is not None:
                if macd > macd_signal:
                    if direction == "BULLISH":
                        confidence += 0.1
                    reasons.append("MACD above signal line")
                elif macd < macd_signal:
                    if direction == "BEARISH":
                        confidence += 0.1
                    reasons.append("MACD below signal line")

            # Bollinger Bands
            bb_upper = signals.get('bb_upper')
            bb_lower = signals.get('bb_lower')
            if bb_upper and bb_lower:
                if current_price > bb_upper:
                    reasons.append("Price above upper Bollinger Band")
                    if direction == "BULLISH":
                        confidence += 0.05
                elif current_price < bb_lower:
                    reasons.append("Price below lower Bollinger Band")
                    if direction == "BEARISH":
                        confidence += 0.05

            # Candlestick Patterns
            latest_doji = signals.get('DOJI', [0])[-1]
            latest_hammer = signals.get('HAMMER', [0])[-1]
            latest_engulfing = signals.get('ENGULFING', [0])[-1]
            latest_morning_star = signals.get('MORNING_STAR', [0])[-1]

            if latest_doji > 0:
                reasons.append("Doji pattern detected - potential reversal")
                confidence += 0.05
            if latest_hammer > 0:
                reasons.append("Hammer pattern detected - bullish reversal")
                if direction != "BEARISH":
                    direction = "BULLISH"
                    confidence += 0.1
            if latest_engulfing > 0:
                reasons.append("Engulfing pattern detected - strong signal")
                confidence += 0.1
            if latest_morning_star > 0:
                reasons.append("Morning Star pattern detected - bullish reversal")
                direction = "BULLISH"
                confidence += 0.15

            # Ensure confidence is between 0 and 1
            confidence = max(0.1, min(0.95, confidence))

            # Calculate entry, stop loss, and target prices
            entry_price = current_price
            if direction == "BULLISH":
                stop_loss = current_price * 0.98  # 2% stop loss
                target = current_price * 1.05     # 5% target
            elif direction == "BEARISH":
                stop_loss = current_price * 1.02  # 2% stop loss
                target = current_price * 0.95     # 5% target
            else:
                stop_loss = current_price * 0.97  # 3% stop loss (wider for neutral)
                target = current_price * 1.03     # 3% target

            signal = {
                "symbol": symbol,
                "direction": direction.lower(),
                "entry_price": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target": round(target, 2),
                "confidence": round(confidence, 2),
                "reasons": reasons,
                "timestamp": datetime.now().isoformat(),
                "indicators": {
                    "rsi": round(signals.get('rsi', 0), 2),
                    "macd": round(signals.get('macd', 0), 2),
                    "sma_20": round(signals.get('sma_20', 0), 2),
                    "sma_50": round(signals.get('sma_50', 0), 2)
                }
            }

            return signal

        except Exception as e:
            logger.error(f"Error generating final signal: {str(e)}")
            return {"error": str(e)}
