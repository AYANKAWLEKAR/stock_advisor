'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, X, Trash2, List, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { apiService } from '@/lib/api';
import { parseStockSymbols } from '@/lib/utils';

export default function StockManager() {
  const [customStocks, setCustomStocks] = useState<string[]>([]);
  const [newStocks, setNewStocks] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    loadCustomStocks();
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const isHealthy = await apiService.checkHealth();
      if (isHealthy) {
        setIsInitialized(true);
      }
    } catch (error) {
      console.error('System check failed:', error);
    }
  };

  const loadCustomStocks = async () => {
    try {
      const result = await apiService.listCustomStocks();
      if (result.success) {
        setCustomStocks(result.custom_stocks);
      }
    } catch (error) {
      console.error('Failed to load custom stocks:', error);
    }
  };

  const handleAddStocks = async () => {
    if (!newStocks.trim()) return;

    const stocks = parseStockSymbols(newStocks);
    if (stocks.length === 0) {
      setMessage({ type: 'error', text: 'Please enter valid stock symbols' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await apiService.addCustomStocks(stocks);
      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: `Successfully added ${result.added?.length || 0} stocks` 
        });
        setNewStocks('');
        await loadCustomStocks();
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to add stocks' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveStock = async (stock: string) => {
    setIsLoading(true);
    setMessage(null);

    try {
      const result = await apiService.removeCustomStocks([stock]);
      if (result.success) {
        setMessage({ type: 'success', text: `Removed ${stock}` });
        await loadCustomStocks();
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to remove stock' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all custom stocks?')) return;

    setIsLoading(true);
    setMessage(null);

    try {
      const result = await apiService.clearCustomStocks();
      if (result.success) {
        setMessage({ type: 'success', text: 'Cleared all custom stocks' });
        await loadCustomStocks();
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to clear stocks' });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isInitialized) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto mb-4" />
            <p className="text-gray-600">Connecting to Stock Advisor API...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Add Stocks Section */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Custom Stocks</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stock Symbols
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={newStocks}
                onChange={(e) => setNewStocks(e.target.value)}
                placeholder="e.g., PLTR, MKL, RBLX or [PLTR, MKL, RBLX]"
                className="flex-1 input-field"
                disabled={isLoading}
              />
              <button
                onClick={handleAddStocks}
                disabled={!newStocks.trim() || isLoading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Enter stock symbols separated by commas. Supports formats like "AAPL, MSFT" or "[AAPL, MSFT]"
            </p>
          </div>

          {message && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-3 rounded-lg flex items-center space-x-2 ${
                message.type === 'success' 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              {message.type === 'success' ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
              <span className={`text-sm ${
                message.type === 'success' ? 'text-green-700' : 'text-red-700'
              }`}>
                {message.text}
              </span>
            </motion.div>
          )}
        </div>
      </div>

      {/* Custom Stocks List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Custom Stocks</h3>
          {customStocks.length > 0 && (
            <button
              onClick={handleClearAll}
              disabled={isLoading}
              className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50 flex items-center space-x-1"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          )}
        </div>

        {customStocks.length === 0 ? (
          <div className="text-center py-8">
            <List className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No custom stocks added yet</p>
            <p className="text-sm text-gray-400">
              Add stocks above to include them in portfolio optimization
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {customStocks.map((stock, index) => (
              <motion.div
                key={stock}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="bg-gray-50 rounded-lg p-3 flex items-center justify-between group hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-xs font-bold text-primary-700">{stock}</span>
                  </div>
                  <span className="font-medium text-gray-900">{stock}</span>
                </div>
                <button
                  onClick={() => handleRemoveStock(stock)}
                  disabled={isLoading}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-100 rounded"
                >
                  <X className="w-4 h-4 text-red-500" />
                </button>
              </motion.div>
            ))}
          </div>
        )}

        {customStocks.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-blue-700">
                {customStocks.length} custom stock{customStocks.length !== 1 ? 's' : ''} will be included in portfolio optimization
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Popular Tech Stocks</h4>
            <p className="text-sm text-gray-600 mb-3">AAPL, MSFT, GOOGL, AMZN, TSLA</p>
            <button
              onClick={() => setNewStocks('AAPL, MSFT, GOOGL, AMZN, TSLA')}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Add These →
            </button>
          </div>
          
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Growth Stocks</h4>
            <p className="text-sm text-gray-600 mb-3">PLTR, RBLX, SNOW, ZM, DOCU</p>
            <button
              onClick={() => setNewStocks('PLTR, RBLX, SNOW, ZM, DOCU')}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Add These →
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
