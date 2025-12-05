import pandas as pd
import numpy as np
from datetime import datetime
import logging
from kite_integration import KiteIntegration

logger = logging.getLogger(__name__)

class OptionAnalyzer:
    def __init__(self, kite_integration):
        self.kite = kite_integration

    def get_option_chain(self, underlying_symbol, expiry_date=None):
        """Get option chain for a given underlying symbol"""
        try:
            instruments = self.kite.get_instruments(exchange="NFO")

            options = []
            for instrument in instruments:
                if (instrument['name'] == underlying_symbol and
                    instrument['instrument_type'] in ['CE', 'PE']):

                    if expiry_date and instrument['expiry'] != expiry_date:
                        continue

                    option_data = {
                        'tradingsymbol': instrument['tradingsymbol'],
                        'strike': instrument['strike'],
                        'instrument_type': instrument['instrument_type'],
                        'expiry': instrument['expiry'],
                        'lot_size': instrument['lot_size']
                    }

                    # Get live quote if available
                    try:
                        quote = self.kite.get_quote(instrument['instrument_token'])
                        option_data.update({
                            'last_price': quote[str(instrument['instrument_token'])]['last_price'],
                            'open': quote[str(instrument['instrument_token'])]['ohlc']['open'],
                            'high': quote[str(instrument['instrument_token'])]['ohlc']['high'],
                            'low': quote[str(instrument['instrument_token'])]['ohlc']['low'],
                            'close': quote[str(instrument['instrument_token'])]['ohlc']['close'],
                            'volume': quote[str(instrument['instrument_token'])]['volume'],
                            'oi': quote[str(instrument['instrument_token'])]['oi']
                        })
                    except:
                        # If quote not available, set defaults
                        option_data.update({
                            'last_price': 0,
                            'open': 0,
                            'high': 0,
                            'low': 0,
                            'close': 0,
                            'volume': 0,
                            'oi': 0
                        })

                    options.append(option_data)

            # Sort by strike price
            options.sort(key=lambda x: x['strike'])

            return options

        except Exception as e:
            logger.error(f"Error fetching option chain: {str(e)}")
            raise

    def analyze_option_chain(self, underlying_symbol, current_price, expiry_date=None):
        """Analyze option chain and provide insights"""
        try:
            options = self.get_option_chain(underlying_symbol, expiry_date)

            if not options:
                return {"error": "No options found for the symbol"}

            # Separate calls and puts
            calls = [opt for opt in options if opt['instrument_type'] == 'CE']
            puts = [opt for opt in options if opt['instrument_type'] == 'PE']

            # Find at-the-money options
            atm_strike = min(options, key=lambda x: abs(x['strike'] - current_price))['strike']

            # Calculate open interest analysis
            total_call_oi = sum(call.get('oi', 0) for call in calls)
            total_put_oi = sum(put.get('oi', 0) for put in puts)

            # PCR (Put-Call Ratio)
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

            # Find highest OI strikes
            calls_with_oi = [call for call in calls if call.get('oi', 0) > 0]
            puts_with_oi = [put for put in puts if put.get('oi', 0) > 0]

            max_call_oi_strike = max(calls_with_oi, key=lambda x: x['oi'])['strike'] if calls_with_oi else None
            max_put_oi_strike = max(puts_with_oi, key=lambda x: x['oi'])['strike'] if puts_with_oi else None

            # Calculate implied volatility (simplified)
            # In a real implementation, you'd calculate IV using Black-Scholes model
            avg_call_volume = np.mean([call.get('volume', 0) for call in calls])
            avg_put_volume = np.mean([put.get('volume', 0) for put in puts])

            # Market direction hints based on OI and PCR
            market_direction = "NEUTRAL"
            confidence = 0.5

            if pcr > 1.2:
                market_direction = "BEARISH"
                confidence = min(pcr / 2, 0.9)
            elif pcr < 0.8:
                market_direction = "BULLISH"
                confidence = min(1 / pcr, 0.9)

            # Additional checks
            if max_call_oi_strike and max_put_oi_strike:
                if max_call_oi_strike > max_put_oi_strike:
                    market_direction = "BULLISH"
                    confidence = max(confidence, 0.7)
                elif max_put_oi_strike > max_call_oi_strike:
                    market_direction = "BEARISH"
                    confidence = max(confidence, 0.7)

            # Find optimal strike prices for trading
            optimal_strikes = self.find_optimal_strikes(options, current_price, market_direction)

            analysis = {
                'underlying_symbol': underlying_symbol,
                'current_price': current_price,
                'atm_strike': atm_strike,
                'market_direction': market_direction,
                'confidence': confidence,
                'pcr': pcr,
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'max_call_oi_strike': max_call_oi_strike,
                'max_put_oi_strike': max_put_oi_strike,
                'avg_call_volume': avg_call_volume,
                'avg_put_volume': avg_put_volume,
                'optimal_strikes': optimal_strikes,
                'recommendations': self.generate_recommendations(market_direction, optimal_strikes, current_price)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing option chain: {str(e)}")
            raise

    def find_optimal_strikes(self, options, current_price, market_direction):
        """Find optimal strike prices for trading based on analysis"""
        try:
            calls = [opt for opt in options if opt['instrument_type'] == 'CE']
            puts = [opt for opt in options if opt['instrument_type'] == 'PE']

            optimal_strikes = {}

            if market_direction == "BULLISH":
                # For bullish market, look for call options with good OI and reasonable premium
                suitable_calls = [call for call in calls
                                if call['strike'] >= current_price * 0.98 and
                                call['strike'] <= current_price * 1.05 and
                                call.get('oi', 0) > 0]

                if suitable_calls:
                    # Sort by OI and select top 3
                    suitable_calls.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['calls'] = suitable_calls[:3]

                # For hedging, look for put options slightly OTM
                suitable_puts = [put for put in puts
                               if put['strike'] >= current_price * 0.95 and
                               put['strike'] <= current_price * 0.98]

                if suitable_puts:
                    suitable_puts.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['puts'] = suitable_puts[:2]

            elif market_direction == "BEARISH":
                # For bearish market, look for put options with good OI
                suitable_puts = [put for put in puts
                               if put['strike'] <= current_price * 1.02 and
                               put['strike'] >= current_price * 0.95 and
                               put.get('oi', 0) > 0]

                if suitable_puts:
                    suitable_puts.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['puts'] = suitable_puts[:3]

                # For hedging, look for call options slightly OTM
                suitable_calls = [call for call in calls
                                if call['strike'] >= current_price * 1.02 and
                                call['strike'] <= current_price * 1.05]

                if suitable_calls:
                    suitable_calls.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['calls'] = suitable_calls[:2]

            else:  # NEUTRAL
                # For neutral market, look for both calls and puts around ATM
                atm_range = current_price * 0.02  # 2% range

                suitable_calls = [call for call in calls
                                if abs(call['strike'] - current_price) <= atm_range and
                                call.get('oi', 0) > 0]

                suitable_puts = [put for put in puts
                               if abs(put['strike'] - current_price) <= atm_range and
                               put.get('oi', 0) > 0]

                if suitable_calls:
                    suitable_calls.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['calls'] = suitable_calls[:2]

                if suitable_puts:
                    suitable_puts.sort(key=lambda x: x.get('oi', 0), reverse=True)
                    optimal_strikes['puts'] = suitable_puts[:2]

            return optimal_strikes

        except Exception as e:
            logger.error(f"Error finding optimal strikes: {str(e)}")
            return {}

    def generate_recommendations(self, market_direction, optimal_strikes, current_price):
        """Generate trading recommendations based on analysis"""
        try:
            recommendations = []

            if market_direction == "BULLISH":
                recommendations.append({
                    'type': 'CALL_BUY',
                    'description': 'Market shows bullish signals. Consider buying call options.',
                    'strikes': [strike['strike'] for strike in optimal_strikes.get('calls', [])],
                    'risk_level': 'MEDIUM',
                    'expected_move': f"Target: {current_price * 1.05:.2f}"
                })

                if 'puts' in optimal_strikes:
                    recommendations.append({
                        'type': 'PUT_SELL',
                        'description': 'Consider selling put options for additional income.',
                        'strikes': [strike['strike'] for strike in optimal_strikes['puts']],
                        'risk_level': 'LOW',
                        'expected_move': f"Support: {current_price * 0.98:.2f}"
                    })

            elif market_direction == "BEARISH":
                recommendations.append({
                    'type': 'PUT_BUY',
                    'description': 'Market shows bearish signals. Consider buying put options.',
                    'strikes': [strike['strike'] for strike in optimal_strikes.get('puts', [])],
                    'risk_level': 'MEDIUM',
                    'expected_move': f"Target: {current_price * 0.95:.2f}"
                })

                if 'calls' in optimal_strikes:
                    recommendations.append({
                        'type': 'CALL_SELL',
                        'description': 'Consider selling call options for additional income.',
                        'strikes': [strike['strike'] for strike in optimal_strikes['calls']],
                        'risk_level': 'LOW',
                        'expected_move': f"Resistance: {current_price * 1.02:.2f}"
                    })

            else:  # NEUTRAL
                recommendations.append({
                    'type': 'STRADDLE',
                    'description': 'Market is neutral. Consider buying both call and put at same strike.',
                    'strikes': [current_price],
                    'risk_level': 'HIGH',
                    'expected_move': f"Breakout above: {current_price * 1.03:.2f} or below: {current_price * 0.97:.2f}"
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
