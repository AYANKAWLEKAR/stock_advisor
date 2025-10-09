'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart3, DollarSign, PieChart, AlertTriangle } from 'lucide-react';
import { formatCurrency, formatPercentage, formatNumber } from '@/lib/utils';
import { Portfolio, BacktestResults } from '@/lib/api';

interface PortfolioDisplayProps {
  portfolio: Portfolio;
  backtest: BacktestResults;
  selectedStocks: string[];
}

export default function PortfolioDisplay({ portfolio, backtest, selectedStocks }: PortfolioDisplayProps) {
  const sortedAllocations = Object.entries(portfolio.allocations)
    .sort(([, a], [, b]) => b.weight - a.weight);

  const riskColor = portfolio.volatility < 0.15 ? 'text-green-600' : 
                   portfolio.volatility < 0.25 ? 'text-yellow-600' : 'text-red-600';

  const riskLevel = portfolio.volatility < 0.15 ? 'Low Risk' : 
                   portfolio.volatility < 0.25 ? 'Medium Risk' : 'High Risk';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Portfolio Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Portfolio Summary</h2>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${riskColor.replace('text-', 'bg-')}`}></div>
            <span className={`text-sm font-medium ${riskColor}`}>{riskLevel}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <DollarSign className="w-4 h-4 text-primary-500" />
              <span className="text-sm font-medium text-gray-600">Total Investment</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(portfolio.total_investment)}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-gray-600">Expected Return</span>
            </div>
            <p className="text-2xl font-bold text-green-600">{formatPercentage(portfolio.expected_return)}</p>
            {portfolio.net_return && (
              <p className="text-xs text-gray-500">Net: {formatPercentage(portfolio.net_return)}</p>
            )}
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-gray-600">Volatility</span>
            </div>
            <p className={`text-2xl font-bold ${riskColor}`}>{formatPercentage(portfolio.volatility)}</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <PieChart className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium text-gray-600">Sharpe Ratio</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(portfolio.sharpe_ratio)}</p>
            {portfolio.net_sharpe_ratio && (
              <p className="text-xs text-gray-500">Net: {formatNumber(portfolio.net_sharpe_ratio)}</p>
            )}
          </div>
        </div>
      </div>

      {/* Stock Allocations */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Allocations</h3>
        <div className="space-y-3">
          {sortedAllocations.map(([stock, allocation], index) => (
            <motion.div
              key={stock}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold text-primary-700">{stock}</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{stock}</p>
                  <p className="text-sm text-gray-500">{allocation.shares} shares</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">{formatPercentage(allocation.weight)}</p>
                <p className="text-sm text-gray-500">{formatCurrency(allocation.dollar_amount)}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Historical Performance */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Historical Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Total Return</span>
            </div>
            <p className="text-xl font-bold text-green-600">{formatPercentage(backtest.total_return)}</p>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">Annual Return</span>
            </div>
            <p className="text-xl font-bold text-blue-600">{formatPercentage(backtest.annual_return)}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <PieChart className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-700">Sharpe Ratio</span>
            </div>
            <p className="text-xl font-bold text-purple-600">{formatNumber(backtest.sharpe_ratio)}</p>
          </div>

          <div className="bg-red-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-700">Max Drawdown</span>
            </div>
            <p className="text-xl font-bold text-red-600">{formatPercentage(backtest.max_drawdown)}</p>
          </div>
        </div>
      </div>

      {/* Risk Warning */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
      >
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-yellow-800">Investment Disclaimer</h4>
            <p className="text-sm text-yellow-700 mt-1">
              These are algorithmic recommendations based on historical data. Past performance does not guarantee future results. 
              Please consult with a financial advisor before making investment decisions.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
