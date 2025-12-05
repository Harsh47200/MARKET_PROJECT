// Stock Market Analysis Tool Frontend
class StockAnalyzer {
    constructor() {
        this.currentSymbol = 'NIFTY';
        this.apiBaseUrl = 'http://localhost:5000';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadMarketData();
        this.loadSignals();
        this.loadOptionsAnalysis();
        this.startAutoRefresh();
    }

    bindEvents() {
        // Navigation buttons
        document.getElementById('nifty-btn').addEventListener('click', () => this.switchSymbol('NIFTY'));
        document.getElementById('banknifty-btn').addEventListener('click', () => this.switchSymbol('BANKNIFTY'));
        document.getElementById('sensex-btn').addEventListener('click', () => this.switchSymbol('SENSEX'));

        // Modal close button
        document.querySelector('.close').addEventListener('click', () => this.closeModal());

        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('chart-modal');
            if (event.target === modal) {
                this.closeModal();
            }
        });
    }

    switchSymbol(symbol) {
        this.currentSymbol = symbol;

        // Update active button
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${symbol.toLowerCase()}-btn`).classList.add('active');

        // Reload data
        this.loadMarketData();
        this.loadSignals();
        this.loadOptionsAnalysis();
        this.loadOptionChain();
    }

    async loadMarketData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/market_data/${this.currentSymbol}`);
            const data = await response.json();

            if (data.error) {
                this.showError('market-data', data.error);
                return;
            }

            this.updateMarketCards(data);
        } catch (error) {
            console.error('Error loading market data:', error);
            this.showError('market-data', 'Failed to load market data');
        }
    }

    updateMarketCards(data) {
        const instruments = data.data || {};

        // Update each symbol's card
        ['NIFTY', 'BANKNIFTY', 'SENSEX'].forEach(symbol => {
            const card = document.getElementById(`${symbol.toLowerCase()}-card`);
            const priceEl = document.getElementById(`${symbol.toLowerCase()}-price`);
            const changeEl = document.getElementById(`${symbol.toLowerCase()}-change`);

            if (instruments[symbol]) {
                const instrument = instruments[symbol];
                const lastPrice = instrument.last_price;
                const netChange = instrument.net_change || 0;

                priceEl.textContent = lastPrice ? lastPrice.toFixed(2) : '--';
                changeEl.textContent = netChange ? `${netChange > 0 ? '+' : ''}${netChange.toFixed(2)} (${((netChange / (lastPrice - netChange)) * 100).toFixed(2)}%)` : '--';

                changeEl.className = netChange > 0 ? 'change positive' : netChange < 0 ? 'change negative' : 'change';
            } else {
                priceEl.textContent = '--';
                changeEl.textContent = '--';
                changeEl.className = 'change';
            }
        });
    }

    async loadSignals() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/signals/${this.currentSymbol}`);
            const data = await response.json();

            if (data.error) {
                this.showError('signals', data.error);
                return;
            }

            this.updateSignals(data);
        } catch (error) {
            console.error('Error loading signals:', error);
            this.showError('signals', 'Failed to load signals');
        }
    }

    updateSignals(data) {
        document.getElementById('signal-symbol').textContent = data.symbol || this.currentSymbol;
        document.getElementById('signal-direction').textContent = data.direction || 'neutral';
        document.getElementById('signal-direction').className = `signal-direction ${data.direction || 'neutral'}`;

        document.getElementById('entry-price').textContent = data.entry_price ? `₹${data.entry_price}` : '--';
        document.getElementById('stop-loss').textContent = data.stop_loss ? `₹${data.stop_loss}` : '--';
        document.getElementById('target-price').textContent = data.target ? `₹${data.target}` : '--';
        document.getElementById('confidence').textContent = data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : '--';

        // Update indicators
        const indicators = data.indicators || {};
        document.getElementById('rsi').textContent = indicators.rsi ? indicators.rsi.toFixed(2) : '--';
        document.getElementById('macd').textContent = indicators.macd ? indicators.macd.toFixed(2) : '--';
        document.getElementById('sma20').textContent = indicators.sma_20 ? indicators.sma_20.toFixed(2) : '--';
        document.getElementById('sma50').textContent = indicators.sma_50 ? indicators.sma_50.toFixed(2) : '--';

        // Update reasons
        const reasonsList = document.getElementById('signal-reasons');
        reasonsList.innerHTML = '';

        if (data.reasons && data.reasons.length > 0) {
            const ul = document.createElement('ul');
            data.reasons.forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                ul.appendChild(li);
            });
            reasonsList.appendChild(ul);
        } else {
            reasonsList.innerHTML = '<p>No specific reasons available</p>';
        }
    }

    async loadOptionsAnalysis() {
        try {
            // For now, we'll simulate options analysis since the endpoint might not be fully implemented
            // In a real implementation, you'd call: fetch(`${this.apiBaseUrl}/option_analysis/${this.currentSymbol}`)
            const mockData = {
                market_direction: 'BULLISH',
                confidence: 0.75,
                pcr: 1.25,
                max_call_oi_strike: 18000,
                max_put_oi_strike: 17900,
                recommendations: [
                    {
                        type: 'CALL_BUY',
                        description: 'Market shows bullish signals. Consider buying call options.',
                        strikes: [18000, 18100],
                        risk_level: 'MEDIUM'
                    }
                ]
            };

            this.updateOptionsAnalysis(mockData);
        } catch (error) {
            console.error('Error loading options analysis:', error);
            this.showError('options', 'Failed to load options analysis');
        }
    }

    updateOptionsAnalysis(data) {
        document.getElementById('market-direction').textContent = data.market_direction || '--';
        document.getElementById('pcr').textContent = data.pcr ? data.pcr.toFixed(2) : '--';
        document.getElementById('max-call-oi').textContent = data.max_call_oi_strike || '--';
        document.getElementById('max-put-oi').textContent = data.max_put_oi_strike || '--';

        // Update recommendations
        const recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = '<h4>Trading Recommendations</h4>';

        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const recDiv = document.createElement('div');
                recDiv.className = 'recommendation-item';

                recDiv.innerHTML = `
                    <h5>${rec.type.replace('_', ' ')}</h5>
                    <p>${rec.description}</p>
                    <div class="strikes">Recommended Strikes: ${rec.strikes.join(', ')}</div>
                    <small>Risk Level: ${rec.risk_level}</small>
                `;

                recommendationsDiv.appendChild(recDiv);
            });
        } else {
            recommendationsDiv.innerHTML += '<p>No recommendations available at this time.</p>';
        }
    }

    showError(section, message) {
        console.error(`Error in ${section}: ${message}`);

        // Show user-friendly error messages
        switch(section) {
            case 'market-data':
                ['nifty', 'banknifty', 'sensex'].forEach(symbol => {
                    document.getElementById(`${symbol}-price`).textContent = 'Error';
                    document.getElementById(`${symbol}-change`).textContent = message;
                });
                break;
            case 'signals':
                document.getElementById('signal-symbol').textContent = 'Error loading signals';
                break;
            case 'options':
                document.getElementById('market-direction').textContent = 'Error';
                break;
            case 'option-chain':
                document.getElementById('option-chain-table').innerHTML = `<p>Error loading option chain: ${message}</p>`;
                break;
        }
    }

    async loadOptionChain() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/option_chain/${this.currentSymbol}`);
            const data = await response.json();

            if (data.error) {
                this.showError('option-chain', data.error);
                return;
            }

            this.updateOptionChain(data);
        } catch (error) {
            console.error('Error loading option chain:', error);
            this.showError('option-chain', 'Failed to load option chain');
        }
    }

    updateOptionChain(options) {
        const tableContainer = document.getElementById('option-chain-table');
        tableContainer.innerHTML = '';

        if (!options || options.length === 0) {
            tableContainer.innerHTML = '<p>No option chain data available</p>';
            return;
        }

        // Create header
        const header = document.createElement('div');
        header.className = 'option-chain-header';
        header.innerHTML = `
            <div class="calls">CALLS</div>
            <div class="strike">STRIKE</div>
            <div class="puts">PUTS</div>
        `;
        tableContainer.appendChild(header);

        // Group options by strike price
        const strikeGroups = {};
        options.forEach(option => {
            const strike = option.strike;
            if (!strikeGroups[strike]) {
                strikeGroups[strike] = { calls: [], puts: [] };
            }
            if (option.instrument_type === 'CE') {
                strikeGroups[strike].calls.push(option);
            } else if (option.instrument_type === 'PE') {
                strikeGroups[strike].puts.push(option);
            }
        });

        // Get current price for ATM calculation
        const currentPrice = this.getCurrentPrice();

        // Sort strikes and create rows
        const sortedStrikes = Object.keys(strikeGroups).sort((a, b) => parseFloat(a) - parseFloat(b));

        sortedStrikes.forEach(strike => {
            const group = strikeGroups[strike];
            const isATM = currentPrice && Math.abs(parseFloat(strike) - currentPrice) < 50; // Within 50 points

            const row = document.createElement('div');
            row.className = 'option-chain-row';

            // Calls column
            const callsDiv = document.createElement('div');
            callsDiv.className = 'calls';
            if (group.calls.length > 0) {
                const call = group.calls[0]; // Take first call option
                callsDiv.innerHTML = `
                    <div class="option-data" onclick="app.showCandlestickChart('${call.tradingsymbol}', ${strike}, 'CALL')">
                        <div class="option-price">₹${call.last_price || 0}</div>
                        <div class="option-oi">OI: ${call.oi || 0}</div>
                        <div class="option-volume">Vol: ${call.volume || 0}</div>
                    </div>
                `;
            }
            row.appendChild(callsDiv);

            // Strike column
            const strikeDiv = document.createElement('div');
            strikeDiv.className = `strike-price ${isATM ? 'atm' : ''}`;
            strikeDiv.textContent = strike;
            strikeDiv.onclick = () => this.showCandlestickChart(`${this.currentSymbol}${strike}`, strike, 'STRIKE');
            row.appendChild(strikeDiv);

            // Puts column
            const putsDiv = document.createElement('div');
            putsDiv.className = 'puts';
            if (group.puts.length > 0) {
                const put = group.puts[0]; // Take first put option
                putsDiv.innerHTML = `
                    <div class="option-data" onclick="app.showCandlestickChart('${put.tradingsymbol}', ${strike}, 'PUT')">
                        <div class="option-price">₹${put.last_price || 0}</div>
                        <div class="option-oi">OI: ${put.oi || 0}</div>
                        <div class="option-volume">Vol: ${put.volume || 0}</div>
                    </div>
                `;
            }
            row.appendChild(putsDiv);

            tableContainer.appendChild(row);
        });
    }

    getCurrentPrice() {
        // Get current price from the market data cards
        const priceEl = document.getElementById(`${this.currentSymbol.toLowerCase()}-price`);
        if (priceEl && priceEl.textContent !== '--') {
            return parseFloat(priceEl.textContent);
        }
        return null;
    }

    showCandlestickChart(symbol, strike, type) {
        document.getElementById('chart-title').textContent = `${symbol} - ${type} Candlestick Chart`;
        document.getElementById('chart-modal').style.display = 'block';

        // For demo purposes, we'll create a mock candlestick chart
        // In a real implementation, you'd fetch historical data for the specific option
        this.createMockCandlestickChart();
    }

    createMockCandlestickChart() {
        const ctx = document.getElementById('candlestick-chart').getContext('2d');

        // Mock data for demonstration - using line chart instead of candlestick
        const data = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Price Movement',
                data: [105, 110, 115, 120, 125, 130],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            }]
        };

        new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Mock Candlestick Chart (Demo Data)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    }
                }
            }
        });
    }

    closeModal() {
        document.getElementById('chart-modal').style.display = 'none';
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadMarketData();
            this.loadSignals();
            this.loadOptionsAnalysis();
        }, 30000);
    }
}

// Global app instance
let app;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app = new StockAnalyzer();
});

// Add loading indicators
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"></div>';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element && element.querySelector('.loading')) {
        element.innerHTML = '';
    }
}
