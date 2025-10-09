'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, BarChart3, Settings, Home, Bot } from 'lucide-react';
import Header from '@/components/Header';
import ChatInterface from '@/components/ChatInterface';
import PortfolioDisplay from '@/components/PortfolioDisplay';
import StockManager from '@/components/StockManager';

type TabType = 'chat' | 'portfolio' | 'stocks';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [portfolioData, setPortfolioData] = useState<any>(null);

  const tabs = [
    { id: 'chat' as const, label: 'AI Chat', icon: MessageCircle },
    { id: 'portfolio' as const, label: 'Portfolio', icon: BarChart3 },
    { id: 'stocks' as const, label: 'Manage Stocks', icon: Settings },
  ];

  const handlePortfolioUpdate = (data: any) => {
    setPortfolioData(data);
    setActiveTab('portfolio');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">AI Stock Advisor</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get personalized stock recommendations powered by AI. Add custom stocks, analyze market clusters, 
            and optimize your portfolio with advanced risk management.
          </p>
        </motion.div>

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6"
        >
          <div className="flex border-b border-gray-200">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 transition-colors ${
                    activeTab === tab.id
                      ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'chat' && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-xl shadow-sm border border-gray-200 h-[600px]"
            >
              <ChatInterface onPortfolioUpdate={handlePortfolioUpdate} />
            </motion.div>
          )}

          {activeTab === 'portfolio' && (
            <motion.div
              key="portfolio"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {portfolioData ? (
                <PortfolioDisplay
                  portfolio={portfolioData.portfolio}
                  backtest={portfolioData.backtest}
                  selectedStocks={portfolioData.selectedStocks}
                />
              ) : (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                  <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Portfolio Data</h3>
                  <p className="text-gray-600 mb-6">
                    Get personalized stock recommendations through the AI Chat to see your portfolio analysis here.
                  </p>
                  <button
                    onClick={() => setActiveTab('chat')}
                    className="btn-primary"
                  >
                    Start Chat
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'stocks' && (
            <motion.div
              key="stocks"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <StockManager />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600">
              Advanced algorithms analyze market data and provide intelligent stock recommendations based on your risk tolerance.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk-Based Optimization</h3>
            <p className="text-gray-600">
              Capital-aware portfolio optimization that considers transaction costs and investment amounts for realistic recommendations.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <Settings className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Custom Stock Management</h3>
            <p className="text-gray-600">
              Add your favorite stocks to the portfolio analysis. Include any publicly traded stocks for personalized recommendations.
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
