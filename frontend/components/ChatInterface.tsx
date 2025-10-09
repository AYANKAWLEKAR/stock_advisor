'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, AlertCircle } from 'lucide-react';
import { apiService, Message } from '@/lib/api';
import { generateId, formatTimestamp } from '@/lib/utils';

interface ChatInterfaceProps {
  onPortfolioUpdate?: (data: any) => void;
}

export default function ChatInterface({ onPortfolioUpdate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      type: 'agent',
      content: 'Hello! I\'m your AI Stock Advisor. I can help you with:\n\n• Adding custom stocks to your portfolio\n• Getting personalized stock recommendations\n• Analyzing market clusters\n• Managing your investment strategy\n\nWhat would you like to do today?',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Process the message and get AI response
      const response = await processMessage(userMessage.content);
      
      const agentMessage: Message = {
        id: generateId(),
        type: 'agent',
        content: response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      
      const errorMessage: Message = {
        id: generateId(),
        type: 'agent',
        content: 'I apologize, but I encountered an error. Please try again or check if the API is running.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const processMessage = async (message: string): Promise<string> => {
    const lowerMessage = message.toLowerCase();

    // Initialize system
    if (lowerMessage.includes('initialize') || lowerMessage.includes('start')) {
      try {
        const result = await apiService.initializeSystem();
        if (result.success) {
          return `System initialized successfully! I've analyzed ${Object.keys(result.clusters).length} stock clusters. You can now get personalized recommendations or add custom stocks to your portfolio.`;
        } else {
          return `Initialization failed: ${result.message}`;
        }
      } catch (error) {
        throw new Error('Failed to initialize the system');
      }
    }

    // Add custom stocks
    if (lowerMessage.includes('add') && (lowerMessage.includes('stock') || lowerMessage.includes('['))) {
      const stockSymbols = extractStockSymbols(message);
      if (stockSymbols.length > 0) {
        try {
          const result = await apiService.addCustomStocks(stockSymbols);
          if (result.success) {
            let response = `Successfully added ${result.added?.length || 0} custom stocks to your portfolio.`;
            if (result.added && result.added.length > 0) {
              response += ` Added: ${result.added.join(', ')}.`;
            }
            if (result.failed && result.failed.length > 0) {
              response += ` Failed: ${result.failed.join(', ')}.`;
            }
            response += ` Total custom stocks: ${result.total_custom_stocks}.`;
            return response;
          } else {
            return `Failed to add stocks: ${result.message}`;
          }
        } catch (error) {
          throw new Error('Failed to add custom stocks');
        }
      }
    }

    // Get recommendations
    if (lowerMessage.includes('recommend') || lowerMessage.includes('portfolio') || lowerMessage.includes('invest')) {
      const riskTolerance = extractRiskTolerance(lowerMessage);
      const investmentAmount = extractInvestmentAmount(message);
      
      try {
        const result = await apiService.getRecommendations(riskTolerance, investmentAmount);
        if (result.success) {
          onPortfolioUpdate?.(result);
          return formatPortfolioResponse(result);
        } else {
          return `Failed to get recommendations: ${result.message}`;
        }
      } catch (error) {
        throw new Error('Failed to get recommendations');
      }
    }

    // List custom stocks
    if (lowerMessage.includes('list') && lowerMessage.includes('stock')) {
      try {
        const result = await apiService.listCustomStocks();
        if (result.success) {
          if (result.custom_stocks.length > 0) {
            return `Your custom stocks: ${result.custom_stocks.join(', ')}. Total: ${result.total_custom_stocks} custom stocks out of ${result.total_available_stocks} available.`;
          } else {
            return `No custom stocks added yet. You can add stocks using: "Add the following stocks: [SYMBOL1, SYMBOL2, ...]"`;
          }
        } else {
          return 'Failed to get custom stocks list';
        }
      } catch (error) {
        throw new Error('Failed to get custom stocks list');
      }
    }

    // Default response
    return `I understand you want help with: "${message}". I can assist you with:\n\n• Adding custom stocks: "Add the following stocks: [AAPL, MSFT, GOOGL]"\n• Getting recommendations: "I want conservative recommendations for $10,000"\n• Analyzing clusters: "Show me the market clusters"\n• Managing stocks: "List my custom stocks"\n\nWhat specific action would you like me to help you with?`;
  };

  const extractStockSymbols = (text: string): string[] => {
    const bracketMatch = text.match(/\[([^\]]+)\]/);
    if (bracketMatch) {
      return bracketMatch[1].split(',').map(s => s.trim().toUpperCase());
    }
    return [];
  };

  const extractRiskTolerance = (text: string): string => {
    if (text.includes('conservative') || text.includes('safe')) return 'conservative';
    if (text.includes('aggressive') || text.includes('growth')) return 'aggressive';
    return 'balanced';
  };

  const extractInvestmentAmount = (text: string): number => {
    const match = text.match(/\$?([\d,]+(?:\.\d{2})?)/);
    if (match) {
      return parseFloat(match[1].replace(',', ''));
    }
    return 10000;
  };

  const formatPortfolioResponse = (result: any): string => {
    const { portfolio, backtest } = result;
    return `Here's your personalized portfolio recommendation:

**Portfolio Summary:**
• Total Investment: $${portfolio.total_investment.toLocaleString()}
• Expected Annual Return: ${(portfolio.expected_return * 100).toFixed(2)}%
• Portfolio Volatility: ${(portfolio.volatility * 100).toFixed(2)}%
• Sharpe Ratio: ${portfolio.sharpe_ratio.toFixed(2)}

**Top Allocations:**
${Object.entries(portfolio.allocations)
  .slice(0, 5)
  .map(([stock, allocation]: [string, any]) => 
    `• ${stock}: ${(allocation.weight * 100).toFixed(1)}% (${allocation.shares} shares)`
  ).join('\n')}

**Historical Performance:**
• Total Return: ${(backtest.total_return * 100).toFixed(2)}%
• Annual Return: ${(backtest.annual_return * 100).toFixed(2)}%
• Max Drawdown: ${(backtest.max_drawdown * 100).toFixed(2)}%

Please consult with a financial advisor before making investment decisions.`;
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-4xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                <div className={`chat-message ${
                  message.type === 'user' ? 'chat-user' : 'chat-agent'
                }`}>
                  <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                  <div className="text-xs text-gray-500 mt-2">
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="chat-message chat-agent">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-4 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2"
        >
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span className="text-sm text-red-700">{error}</span>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex space-x-3">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me about stocks, portfolios, or add custom stocks..."
            className="flex-1 input-field"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
