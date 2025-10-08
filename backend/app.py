import os
import pandas as pd
from flask import Flask
from flask import jsonify, request, abort
from flask_cors import CORS 
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize
import numpy as np
#from json import jsonify


app = Flask(__name__)
CORS(app)

class StockAdvisor:
    def __init__(self):
        self.sp500_symbols = [
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ', 'V',
            'WMT', 'JPM', 'MA', 'PG', 'HD', 'CVX', 'LLY', 'ABBV', 'PFE', 'KO',
            'PEP', 'AVGO', 'TMO', 'COST', 'MRK', 'BAC', 'XOM', 'DIS', 'ABT', 'CRM',
            'NFLX', 'VZ', 'ADBE', 'WFC', 'T', 'NKE', 'AMD', 'CMCSA', 'BMY', 'TXN',
            'QCOM', 'DHR', 'UPS', 'PM', 'MS', 'HON', 'NEE', 'LOW', 'COP', 'AMGN'
        ]
        self.data = None
        self.returns = None
        self.clusters = None

    def fetch_market_data(self,period):
        ''' fetch historical market data for given stocks, and set self.data'''
        try:
            # Placeholder for actual market data fetching logic
            data = {}
            for symbol in self.sp500_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period)
                    if len(hist) > 252:  # At least 1 year of data
                        data[symbol] = hist['Close']
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    continue
            
            if len(data) < 20:
                raise Exception("Not enough data fetched")
                
            self.data = pd.DataFrame(data).fillna(method='ffill').dropna()
            self.returns = self.data.pct_change().dropna()
            print(f"Successfully fetched data for {len(self.data.columns)} stocks")
            return True
        except Exception as e:
            raise Exception(f"Error fetching market data {e}")
        
    def calculate_metrics(self):
        """Calculate key financial metrics for each stock"""
        if self.returns is None:
            return None
            
        metrics = {}
        for symbol in self.returns.columns:
            returns = self.returns[symbol]
            
            metrics[symbol] = {
                'annual_return': returns.mean() * 252,
                'volatility': returns.std() * np.sqrt(252),
                'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
                'max_drawdown': self.calculate_max_drawdown(symbol),
                'correlation_with_market': returns.corr(self.returns.mean(axis=1))
            }
        
        return pd.DataFrame(metrics).T
    
    def calculate_max_drawdown(self, symbol):
        prices = self.data[symbol]
        cumulative = (1 + self.returns[symbol]).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def perform_clustering(self, n_clusters=6):
        '''USE scikit to cluster stocks based on metrics'''
        metrics_df = self.calculate_metrics()
        if metrics_df is None:
            return None
        
        # Select features 
        features = ['annual_return', 'volatility', 'sharpe_ratio']
        X = metrics_df[features].fillna(0)
        
        # Standardize values 
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        #K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        metrics_df['cluster'] = clusters
        self.clusters = metrics_df
        
        cluster_analysis = {}
        for cluster_id in range(n_clusters):
            cluster_stocks = metrics_df[metrics_df['cluster'] == cluster_id] #values where cluster id matches up
            cluster_analysis[cluster_id] = {
                'stocks': cluster_stocks.index.tolist(), #list of stocks in that cluster
                'avg_return': cluster_stocks['annual_return'].mean(),
                'avg_volatility': cluster_stocks['volatility'].mean(),
                'avg_sharpe': cluster_stocks['sharpe_ratio'].mean(),
                'size': len(cluster_stocks),
                'risk_level': self.categorize_risk_level(cluster_stocks['volatility'].mean())
            }
        
        return cluster_analysis
    
    def categorize_risk_level(self, volatility):
        """Categorize risk level based on volatility"""
        if volatility < 0.15:
            return 'Low'
        elif volatility < 0.25:
            return 'Medium'
        else:
            return 'High'
    
    def optimize_portfolio(self, selected_stocks, risk_tolerance='balanced', investment_amount=10000):
        """Optimize portfolio using Modern Portfolio Theory with capital-aware constraints"""
        """returns optimal weights, expected return, optimal sharpe ratio etc"""
        if not selected_stocks or len(selected_stocks) < 2:
            return None
            
        # Filter returns for selected stocks
        stock_returns = self.returns[selected_stocks].fillna(0)
        
        # Calculate expected returns and covariance matrix
        expected_returns = stock_returns.mean() * 252
        cov_matrix = stock_returns.cov() * 252
        
        # Adjust risk multiplier based on type of risk pursuit
        risk_multiplier = {'conservative': 0.5, 'balanced': 1.0, 'aggressive': 1.5}
        risk_factor = risk_multiplier.get(risk_tolerance, 1.0)
        
        # Calculate transaction costs based on investment 
        # This allows for more realistic portfolio optimization by considering the cost of trading
        transaction_costs = self.calculate_transaction_costs(selected_stocks, investment_amount)
        
        # Calculate minimum viable weights based on investment amount
        min_weights = self.calculate_minimum_weights(selected_stocks, investment_amount)
        
        def objective(weights): # error function of sharpe ratio given model weights
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            sharpe_ratio = portfolio_return / np.sqrt(portfolio_variance)
            
            # Adjust for transaction costs (net return consideration)
            # This allows for minimization of sharpe ration in more realistic sense
            net_return = portfolio_return - np.sum(weights * transaction_costs)
            
            # Penalize portfolios with too many small positions (diversification cost)
            diversification_penalty = self.calculate_diversification_penalty(weights, investment_amount)
            
            # Final objective: maximize risk-adjusted net return
            adjusted_sharpe = net_return / np.sqrt(portfolio_variance) - diversification_penalty
            return -adjusted_sharpe * risk_factor
        
        # Dynamic bounds based on investment amount
        bounds = self._calculate_dynamic_bounds(selected_stocks, investment_amount, min_weights)
        
        # constraint function (tuple because that's what minimize function takes)
        constraints = {'type': 'eq', 'func': lambda x: np.sum(x) - 1}
        
        initial_guess = np.array([1/len(selected_stocks)] * len(selected_stocks))
        
        # Optimize
        try:
            result = minimize(objective, initial_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            #minimize function using sequential least squares programming
            # result after optimization would contain the ideal weights in the shape of initial guess
            # Enhanced with capital-aware optimization
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(optimal_weights * expected_returns)
                portfolio_variance = np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                sharpe_ratio = portfolio_return / portfolio_volatility
                
                # Calculate net return after transaction costs
                net_return = portfolio_return - np.sum(optimal_weights * transaction_costs)
                net_sharpe = net_return / portfolio_volatility if portfolio_volatility > 0 else 0
                
                return {
                    'weights': dict(zip(selected_stocks, optimal_weights)),
                    'expected_return': portfolio_return,
                    'net_return': net_return,
                    'volatility': portfolio_volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'net_sharpe_ratio': net_sharpe,
                    'transaction_costs': transaction_costs,
                    'investment_amount': investment_amount
                }
        except Exception as e:
            print(f"Optimization error: {e}")
        
        return None
    
    def calculate_transaction_costs(self, selected_stocks, investment_amount):
        """Calculate transaction costs for each stock based on investment amount"""
      
        base_commission = 1.0 if investment_amount < 5000 else 0.0
        
    
        market_impact = 0.0001  # 0.01% for large cap S&P 500 stocks
        
        # Bid-ask spread (average 0.05% for large caps)
        bid_ask_spread = 0.0005
        
        # Total cost per dollar invested
        total_cost_rate = base_commission / (investment_amount / len(selected_stocks)) + market_impact + bid_ask_spread
        
        # Return array of costs for each stock
        return np.full(len(selected_stocks), total_cost_rate)
    
    def calculate_minimum_weights(self, selected_stocks, investment_amount):
        """Calculate minimum viable weights based on investment amount and stock prices for the lower_bounds"""
        min_weights = []
        
        for stock in selected_stocks:
            current_price = self.data[stock].iloc[-1]
            # Minimum investment per stock: enough to buy at least 1 share + transaction costs
            min_investment = current_price + 10  # $10 buffer for transaction costs
            min_weight = min_investment / investment_amount
            min_weights.append(min_weight)
        
        return np.array(min_weights)
    
    def calculate_diversification_penalty(self, weights, investment_amount):
        """Penalize portfolios with too many small positions for smaller investments"""
        # For smaller investments, prefer fewer, larger positions to reduce transaction costs
        num_positions = np.sum(weights > 0.01)  
        
        if investment_amount < 5000:
            # For small investments, penalize having more than 5-7 positions
            if num_positions > 7:
                return 0.01 * (num_positions - 7)
        elif investment_amount < 25000:
            # For medium investments, penalize having more than 10-12 positions
            if num_positions > 12:
                return 0.005 * (num_positions - 12)
        
        return 0.0
    
    def calculate_dynamic_bounds(self, selected_stocks, investment_amount, min_weights):
        """Calculate dynamic bounds based on investment amount"""
        bounds = []
        
        for i, stock in enumerate(selected_stocks):
            min_weight = min_weights[i]
            
            # For smaller investments, allow higher concentration
            if investment_amount < 10000:
                max_weight = 0.5  # Allow up to 50% in one stock for small investments
            elif investment_amount < 50000:
                max_weight = 0.4  # Allow up to 40% for medium investments
            else:
                max_weight = 0.25  # Cap at 25% for large investments
            
            # Ensure max_weight is at least min_weight
            max_weight = max(max_weight, min_weight)
            
            bounds.append((min_weight, max_weight))
        
        return tuple(bounds)
    
    def backtest_portfolio(self, weights, start_date=None, end_date=None):
        """Backtest the portfolio performance"""
        if weights is None:
            return None
        
        # Convert weights dict to series
        weight_series = pd.Series(weights)
        selected_stocks = list(weights.keys())
        
        # Filter data for backtesting period
        backtest_data = self.data[selected_stocks]
        if start_date:
            backtest_data = backtest_data[backtest_data.index >= start_date]
        if end_date:
            backtest_data = backtest_data[backtest_data.index <= end_date]
        
        # Calculate portfolio value over time
        backtest_returns = backtest_data.pct_change().dropna()
        portfolio_returns = backtest_returns.dot(weight_series)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        # Benchmark (S&P 500 approximation)
        benchmark_returns = backtest_returns.mean(axis=1)
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        # Calculate metrics
        total_return = cumulative_returns.iloc[-1] - 1
        annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'cumulative_returns': cumulative_returns.tolist(),
            'dates': cumulative_returns.index.strftime('%Y-%m-%d').tolist(),
            'benchmark_returns': benchmark_cumulative.tolist(),
            'portfolio_returns': portfolio_returns.tolist()
        }
    
advisor=StockAdvisor()

@app.route("/health")
def health_check():
    return {"status": "ok"}
@app.route("/api/init", methods=["POST"])
def init_process():

    """Initialize the  advisor with market data"""
    try:
        success = advisor.fetch_market_data(period="2y")
        if success:
            cluster_analysis = advisor.perform_clustering()
            return jsonify({
                'success': True,
                'message': 'Data initialized successfully',
                'clusters': cluster_analysis,
                'total_stocks': len(advisor.data.columns) if advisor.data is not None else 0
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to fetch market data'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route("/api/clusters", methods=["GET"])
def get_clusters():
    """Get the latest cluster analysis"""
    if advisor.clusters is None:
        return jsonify({'success': False, 'message': 'Data not initialized'}), 400
    
    cluster_analysis = advisor.perform_clustering()
    return jsonify({'success': True, 'clusters': cluster_analysis})

@app.route("/api/recommend", methods=["POST"])
def recommend_stock():
    """ Generate Stock recommendations based on user risk level. Based on risk level choose cluster and optimize portfolio
    to get the best stock. Return list of stocks and their weights.


    Returns: JSON 
    -Success: True or False
    -Message: Error message if any
    -Portfolio:
        -Allocations: Dictionary of stocks and their weights
        -Expected Return: Expected return of the portfolio
        -Volatility: Volatility of the portfolio
        -Sharpe Ratio: Sharpe ratio of the portfolio
        -Total Investment: Total investment amount
    """
    try:
        data = request.json
        risk_tolerance = data.get('risk_tolerance', 'balanced')
        investment_amount = data.get('investment_amount', 10000)
        selected_clusters = data.get('selected_clusters', [])

        if advisor.clusters is None:
            return jsonify({'success': False, 'message': 'Data not initialized'}), 400
        if risk_tolerance == 'conservative':
            # Select from low volatility clusters
            target_volatility = advisor.clusters['volatility'].quantile(0.33)
            selected_stocks = advisor.clusters[advisor.clusters['volatility'] <= target_volatility].index.tolist()[:15]
        elif risk_tolerance == 'aggressive':
            # Select from high return, high volatility clusters
            target_return = advisor.clusters['annual_return'].quantile(0.67)
            selected_stocks = advisor.clusters[advisor.clusters['annual_return'] >= target_return].index.tolist()[:15]
        else:  # balanced
            # Select from middle range
            selected_stocks = advisor.clusters[
                (advisor.clusters['sharpe_ratio'] > advisor.clusters['sharpe_ratio'].median()) &
                (advisor.clusters['volatility'] < advisor.clusters['volatility'].quantile(0.75))
            ].index.tolist()[:15]
        
        if len(selected_stocks) < 5:
            selected_stocks = advisor.clusters.nlargest(10, 'sharpe_ratio').index.tolist()
        
        # Use sharpe ratio minimization to optimize portfolio weights with capital consideration
        optimized_portfolio = advisor.optimize_portfolio(selected_stocks, risk_tolerance, investment_amount)
        
        if optimized_portfolio is None:
            return jsonify({'success': False, 'message': 'Portfolio optimization failed'}), 500
        
        # Calculate dollar allocations
        dollar_weights = {}
        for stock, weight in optimized_portfolio['weights'].items():
            if weight > 0.01:  # Only include weights > 1%
                dollar_weights[stock] = {
                    'weight': weight,
                    'dollar_amount': weight * investment_amount,
                    'shares': int((weight * investment_amount) / advisor.data[stock].iloc[-1])
                }
        
        # Backtest the portfolio
        backtest_results = advisor.backtest_portfolio(optimized_portfolio['weights'])
        
        return jsonify({
            'success': True,
            'portfolio': {
                'allocations': dollar_weights,
                'expected_return': optimized_portfolio['expected_return'],
                'net_return': optimized_portfolio.get('net_return', optimized_portfolio['expected_return']),
                'volatility': optimized_portfolio['volatility'],
                'sharpe_ratio': optimized_portfolio['sharpe_ratio'],
                'net_sharpe_ratio': optimized_portfolio.get('net_sharpe_ratio', optimized_portfolio['sharpe_ratio']),
                'total_investment': investment_amount,
                'transaction_costs': optimized_portfolio.get('transaction_costs', [0] * len(selected_stocks))
            },
            'backtest': backtest_results,
            'selected_stocks': selected_stocks
        })

    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid input data'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
