import axios from "axios";

const API_BASE_URL =
  typeof window !== "undefined" && (window as any).NEXT_PUBLIC_API_URL
    ? (window as any).NEXT_PUBLIC_API_URL
    : "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

export interface PortfolioAllocation {
  weight: number;
  dollar_amount: number;
  shares: number;
}

export interface Portfolio {
  allocations: Record<string, PortfolioAllocation>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  net_return?: number;
  net_sharpe_ratio?: number;
  total_investment: number;
  transaction_costs?: number[];
}

export interface BacktestResults {
  total_return: number;
  annual_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  cumulative_returns: number[];
  dates: string[];
  benchmark_returns: number[];
  portfolio_returns: number[];
}

export interface RecommendationResponse {
  success: boolean;
  portfolio: Portfolio;
  backtest: BacktestResults;
  selected_stocks: string[];
  message?: string;
}

export interface ClusterData {
  size: number;
  avg_return: number;
  avg_volatility: number;
  avg_sharpe: number;
  risk_level: string;
  stocks: string[];
}

export interface ClusterResponse {
  success: boolean;
  clusters: Record<string, ClusterData>;
  message?: string;
}

export interface CustomStockResponse {
  success: boolean;
  message: string;
  added?: string[];
  failed?: string[];
  removed?: string[];
  not_found?: string[];
  total_custom_stocks: number;
}

// API Functions
export const apiService = {
  // Health check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await api.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },

  // Initialize system
  async initializeSystem(): Promise<ClusterResponse> {
    try {
      const response = await api.post('/api/init');
      return response.data;
    } catch (error) {
      console.error('Failed to initialize system:', error);
      throw error;
    }
  },

  // Get clusters
  async getClusters(): Promise<ClusterResponse> {
    try {
      const response = await api.get('/api/clusters');
      return response.data;
    } catch (error) {
      console.error('Failed to get clusters:', error);
      throw error;
    }
  },

  // Get recommendations
  async getRecommendations(
    riskTolerance: string,
    investmentAmount: number,
    investmentGoals?: string
  ): Promise<RecommendationResponse> {
    try {
      const response = await api.post('/api/recommend', {
        risk_tolerance: riskTolerance,
        investment_amount: investmentAmount,
        investment_goals: investmentGoals,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get recommendations:', error);
      throw error;
    }
  },

  // Add custom stocks
  async addCustomStocks(stocks: string[]): Promise<CustomStockResponse> {
    try {
      const response = await api.post('/api/stocks/add', { stocks });
      return response.data;
    } catch (error) {
      console.error('Failed to add custom stocks:', error);
      throw error;
    }
  },

  // Remove custom stocks
  async removeCustomStocks(stocks: string[]): Promise<CustomStockResponse> {
    try {
      const response = await api.post('/api/stocks/remove', { stocks });
      return response.data;
    } catch (error) {
      console.error('Failed to remove custom stocks:', error);
      throw error;
    }
  },

  // List custom stocks
  async listCustomStocks(): Promise<{
    success: boolean;
    custom_stocks: string[];
    total_custom_stocks: number;
    total_available_stocks: number;
    sp500_stocks_count: number;
  }> {
    try {
      const response = await api.get('/api/stocks/list');
      return response.data;
    } catch (error) {
      console.error('Failed to list custom stocks:', error);
      throw error;
    }
  },

  // Clear custom stocks
  async clearCustomStocks(): Promise<{
    success: boolean;
    message: string;
    removed_count: number;
  }> {
    try {
      const response = await api.post('/api/stocks/clear');
      return response.data;
    } catch (error) {
      console.error('Failed to clear custom stocks:', error);
      throw error;
    }
  },
};

export default api;
