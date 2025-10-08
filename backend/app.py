import os
import pandas as pd
from flask import Flask
from flask_cors import CORS 
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize
import numpy as np


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
    
    def optimize_portfolio(self, selected_stocks, risk_tolerance='balanced'):
        """Optimize portfolio using Modern Portfolio Theory"""
        """returns optimal weights, expected, return, optimal sharpe ratio etc"""
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
        
        def objective(weights): # error function of sharpe ratio given model weights
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            sharpe_ratio = portfolio_return / np.sqrt(portfolio_variance)
            return -sharpe_ratio * risk_factor
        
        # constraint function (tuple because that's what minimize function takes)
        constraints = {'type': 'eq', 'func': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 0.4) for _ in range(len(selected_stocks)))  # Max 40% weights in any stock
        
        initial_guess = np.array([1/len(selected_stocks)] * len(selected_stocks))
        
        # Optimize
        try:
            result = minimize(objective, initial_guess, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            #minimize function using sequential least squares programming
            # result after optimization would contain the ideal weights in the shape of inital guess
            # I used similart metholodogy for rutgers research
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(optimal_weights * expected_returns)
                portfolio_variance = np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                sharpe_ratio = portfolio_return / portfolio_volatility
                
                return {
                    'weights': dict(zip(selected_stocks, optimal_weights)),
                    'expected_return': portfolio_return,
                    'volatility': portfolio_volatility,
                    'sharpe_ratio': sharpe_ratio
                }
        except Exception as e:
            print(f"Optimization error: {e}")
        
        return None
    
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



        
